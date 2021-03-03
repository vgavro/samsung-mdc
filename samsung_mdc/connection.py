from typing import Union, Sequence, Tuple
from functools import partial
import asyncio

from .exceptions import MDCResponseError


HEADER_CODE = 0xAA
RESPONSE_CMD = 0xFF
ACK_CODE = ord('A')  # 0x41 65
NAK_CODE = ord('N')  # 0x4E 78


def _repr_hex(value):
    # return ' '.join(f'{x:02x}:{x}' for x in value)
    return ' '.join(f'{x:02x}' for x in value)


class MDCConnection:
    reader, writer = None, None

    def __init__(self, ip, port=1515, verbose=False):
        self.ip, self.port = ip, port
        self.verbose = (
            partial(print, f'{ip}:{port}') if verbose is True else verbose)

    async def open(self):
        # opens TCP connection
        self.reader, self.writer = \
            await asyncio.open_connection(self.ip, self.port)

    @property
    def is_opened(self):
        self.writer is not None

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
            if self.verbose:
                self.verbose(f'{self.ip}:{self.port}', 'Connected')

        self.writer.write(payload)
        if self.verbose:
            self.verbose(f'{self.ip}:{self.port}', 'Sent', _repr_hex(payload))
        await self.writer.drain()

        resp = await self.reader.read(4)
        if resp[0] != HEADER_CODE:
            raise MDCResponseError('Unexpected header', resp)
        if resp[1] != RESPONSE_CMD:
            raise MDCResponseError('Unexpected cmd', resp)
        if resp[2] != id:
            raise MDCResponseError('Unexpected id', resp)
        resp += await self.reader.read(resp[3] + 1)
        checksum = sum(resp[1:-1]) % 256
        if checksum != int(resp[-1]):
            raise MDCResponseError('Checksum failed', resp)

        if self.verbose:
            self.verbose(f'{self.ip}:{self.port}', 'Recv', _repr_hex(resp))

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
