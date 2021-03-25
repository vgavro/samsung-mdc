from typing import Union, Sequence, Tuple
from functools import partial
from enum import Enum
import asyncio

from .exceptions import MDCResponseError, MDCTimeoutError


HEADER_CODE = 0xAA
RESPONSE_CMD = 0xFF
ACK_CODE = ord('A')  # 0x41 65
NAK_CODE = ord('N')  # 0x4E 78


def _repr_hex(value):
    # return ' '.join(f'{x:02x}:{x}' for x in value)
    return ' '.join(f'{x:02x}' for x in value)


async def wait_for(aw, timeout, reason):
    try:
        return await asyncio.wait_for(aw, timeout)
    except asyncio.TimeoutError as exc:
        raise MDCTimeoutError(reason) from exc


class MDC_CONNECTION_MODE(Enum):
    TCP = 'tcp'
    SERIAL = 'serial'


class MDCConnection:
    reader, writer = None, None

    def __init__(self, target, mode=MDC_CONNECTION_MODE.TCP, timeout=5,
                 connect_timeout=None, verbose=False, **connection_kwargs):
        self.target = target
        self.mode = MDC_CONNECTION_MODE(mode)
        self.connection_kwargs = connection_kwargs

        self.timeout = timeout
        self.connect_timeout = connect_timeout or timeout
        self.verbose = (
            partial(print, self.target) if verbose is True else verbose)

    async def open(self):
        if self.mode == MDC_CONNECTION_MODE.TCP:
            if isinstance(self.target, (list, tuple)):
                # make target be compatible with socket.__init__
                target, port = self.target
            else:
                target, *port = self.target.split(':')
                port = port and int(port[0]) or 1515
            self.connection_kwargs.setdefault('port', port)

            self.reader, self.writer = \
                await wait_for(
                    asyncio.open_connection(target, **self.connection_kwargs),
                    self.connect_timeout, 'Connect timeout')
        else:
            # Make this package optional
            from serial_asyncio import open_serial_connection

            self.reader, self.writer = \
                await wait_for(
                    open_serial_connection(
                        url=self.target,
                        **self.connection_kwargs),
                    self.connect_timeout, 'Connect timeout')

        if self.verbose:
            self.verbose('Connected')

    @property
    def is_opened(self):
        return self.writer is not None

    async def send(self, cmd: Union[int, Tuple[int, int]], id: int,
                   data: Union[bytes, Sequence] = b''):
        subcmd = None
        if isinstance(cmd, Tuple):
            assert len(cmd) == 2
            cmd, subcmd = cmd
        if subcmd is not None:
            data = bytes([subcmd]) + bytes(data)

        payload = bytes((HEADER_CODE, cmd, id, len(data))) + bytes(data)
        checksum = sum(payload[1:]) % 256
        payload += bytes((checksum,))

        if not self.is_opened:
            await self.open()

        self.writer.write(payload)
        await wait_for(self.writer.drain(), self.timeout, 'Write timeout')
        if self.verbose:
            self.verbose('Sent', _repr_hex(payload))

        resp = await wait_for(self.reader.read(4), self.timeout,
                              'Response header read timeout')
        if not resp:
            raise MDCResponseError('Empty response', resp)
        if resp[0] != HEADER_CODE:
            raise MDCResponseError('Unexpected header', resp)
        if resp[1] != RESPONSE_CMD:
            raise MDCResponseError('Unexpected cmd', resp)
        if resp[2] != id:
            raise MDCResponseError('Unexpected id', resp)
        resp += await wait_for(self.reader.read(resp[3] + 1), self.timeout,
                               'Response data read timeout')
        if self.verbose:
            self.verbose('Recv', _repr_hex(resp))

        checksum = sum(resp[1:-1]) % 256
        if checksum != int(resp[-1]):
            raise MDCResponseError('Checksum failed', resp)

        ack, rcmd, data = resp[4], resp[5], resp[6:-1]
        if ack not in (ACK_CODE, NAK_CODE):
            raise MDCResponseError('Unexpected ACK/NAK', resp)

        return (ack == ACK_CODE, rcmd,
                data[1:] if (ack == ACK_CODE and subcmd is not None) else data)

    async def close(self):
        writer = self.writer
        self.reader, self.writer = None, None
        writer.close()
        await writer.wait_closed()

    async def __aenter__(self):
        if not self.is_opened:
            await self.open()
        return self

    async def __aexit__(self, *args):
        if self.is_opened:
            await self.close()

    def __await__(self):
        return self.__aenter__().__await__()
