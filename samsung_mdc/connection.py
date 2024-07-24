from typing import Union, Sequence, Tuple
from functools import partial
from enum import Enum
import asyncio

from .exceptions import MDCResponseError, MDCReadTimeoutError, \
    MDCTimeoutError, MDCTLSRequired, MDCTLSAuthFailed
from .utils import repr_hex


HEADER_CODE = 0xAA
RESPONSE_CMD = 0xFF
ACK_CODE = ord('A')  # 0x41 65
NAK_CODE = ord('N')  # 0x4E 78


def get_checksum(payload):
    # payload should be without HEADER_CODE
    return sum(payload) % 256


def _normalize_cmd(
    cmd: Union[int, Tuple[int], Tuple[int, Union[int, None]]]
) -> Tuple[int, Union[int, None]]:
    """
    Returns (cmd, subcmd) tuple
    """
    if isinstance(cmd, int):
        return cmd, None
    elif len(cmd) == 1:
        return int(cmd[0]), None
    elif not len(cmd) == 2:
        raise ValueError('cmd tuple should contain only (cmd, subcmd)')
    return int(cmd[0]), None if cmd[1] is None else int(cmd[1])


def pack_payload(
    cmd: Union[int, Tuple[int], Tuple[int, int]],
    display_id: int,
    data: Union[bytes, Sequence] = b''
):
    cmd, subcmd = _normalize_cmd(cmd)
    data = bytes(data)
    if subcmd is not None:
        data = bytes([subcmd]) + data

    payload = (
        bytes([HEADER_CODE, cmd, display_id, len(data)])
        + bytes(data)
    )
    payload += bytes([get_checksum(payload[1:])])
    return payload


def pack_response(
    cmd: Union[int, Tuple[int], Tuple[int, int]],
    display_id: int,
    ack: bool,
    data: Union[bytes, Sequence] = b''
):
    cmd, subcmd = _normalize_cmd(cmd)

    if not ack and len(data) != 1:
        raise ValueError(
            'Data should contain only error code for NAK response', data)

    data = bytes(data)
    if subcmd is not None and ack:
        # subcmd is not sent on NAK in response
        data = bytes([subcmd]) + data

    return pack_payload(
       RESPONSE_CMD, display_id,
       bytes([ACK_CODE if ack else NAK_CODE, cmd]) + data
    )


async def wait_for(aw, timeout, reason):
    try:
        return await asyncio.wait_for(aw, timeout)
    except asyncio.TimeoutError as exc:
        raise MDCTimeoutError(reason) from exc


async def wait_for_read(reader, count, timeout, reason):
    try:
        return await asyncio.wait_for(reader.read(count), timeout)
    except asyncio.TimeoutError as exc:
        raise MDCReadTimeoutError(reason, bytes(reader._buffer)) from exc


class CONNECTION_MODE(Enum):
    TCP = 'tcp'
    SERIAL = 'serial'


class MDCConnection:
    reader, writer = None, None

    def __init__(self, target, mode=CONNECTION_MODE.TCP, timeout=5,
                 connect_timeout=None, verbose=False, **connection_kwargs):
        self.target = target
        self.mode = CONNECTION_MODE(mode)
        self.connection_kwargs = connection_kwargs

        self.timeout = timeout
        self.connect_timeout = connect_timeout or timeout
        self.verbose = (
            partial(print, self.target) if verbose is True else verbose)

    async def open(self):
        connection_kwargs = self.connection_kwargs.copy()
        pin = connection_kwargs.pop('pin', None)

        if self.mode == CONNECTION_MODE.TCP:
            if isinstance(self.target, (list, tuple)):
                # make target be compatible with socket.__init__
                target, port = self.target
            else:
                target, *port = self.target.split(':')
                port = port and int(port[0]) or 1515
            connection_kwargs.setdefault('port', port)

            self.reader, self.writer = \
                await wait_for(
                    asyncio.open_connection(target, **connection_kwargs),
                    self.connect_timeout, 'Connect timeout')

            if self.verbose:
                self.verbose('Connected')

        else:
            # Make this package optional
            from serial_asyncio import open_serial_connection

            self.reader, self.writer = \
                await wait_for(
                    open_serial_connection(
                        url=self.target,
                        **connection_kwargs),
                    self.connect_timeout, 'Connect timeout')

            if self.verbose:
                self.verbose('Connected')

        if pin is not None:
            try:
                await self._start_tls(pin)
            except Exception:
                await self.close()
                raise

    async def _start_tls(self, pin):
        if isinstance(pin, int):
            pin = str(pin).rjust(4, '0').encode()
        elif isinstance(pin, str):
            pin = pin.rjust(4, '0').encode()

        assert self.is_opened

        import ssl
        resp = await wait_for_read(self.reader, 15, self.timeout,
                                   'TLS header read timeout')
        if not resp == b'MDCSTART<<TLS>>':
            raise MDCResponseError('Unexpected TLS header',
                                   resp + self.reader._buffer)
        transport = self.writer.transport
        protocol = transport.get_protocol()
        loop = asyncio.get_event_loop()
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.VerifyMode.CERT_NONE
        ssl_transport = await loop.start_tls(
            transport, protocol, ssl_ctx)
        self.writer._transport = ssl_transport
        self.reader._transport = ssl_transport

        if self.verbose:
            self.verbose('TLS established')

        self.writer.write(pin)
        await wait_for(self.writer.drain(), self.timeout,
                       'Write pin timeout')
        resp = await wait_for_read(self.reader, 15, self.timeout,
                                   'TLS auth read timeout')
        if not resp == b'MDCAUTH<<PASS>>':
            if resp[:14] == b'MDCAUTH<<FAIL:':
                resp += await wait_for_read(self.reader, 5, self.timeout,
                                            'TLS auth fail read timeout')
                if resp[-2:] != b'>>':
                    raise MDCResponseError('Unexpected TLS auth fail response',
                                           resp + self.reader._buffer)
                try:
                    fail_code = int(resp[-6:-2], 16)
                except ValueError:
                    raise MDCResponseError('Unexpected TLS auth fail code',
                                           resp + self.reader._buffer)
                raise MDCTLSAuthFailed(fail_code)
            raise MDCResponseError('Unexpected TLS auth response',
                                   resp + self.reader._buffer)

        if self.verbose:
            self.verbose('TLS authentication passed')

    @property
    def is_opened(self):
        return self.writer is not None

    @property
    def is_tls_started(self):
        return (self.writer and self.writer.transport.__class__.__name__ ==
                '_SSLProtocolTransport')

    async def send(
        self,
        cmd: Union[int, Tuple[int], Tuple[int, int]],
        display_id: int,
        data: Union[bytes, Sequence] = b''
    ):
        cmd, subcmd = _normalize_cmd(cmd)
        payload = pack_payload((cmd, subcmd), display_id, data)

        if not self.is_opened:
            await self.open()

        self.writer.write(payload)
        await wait_for(self.writer.drain(), self.timeout, 'Write timeout')
        if self.verbose:
            self.verbose('Sent', repr_hex(payload))

        resp = await wait_for_read(self.reader, 4, self.timeout,
                                   'Response header read timeout')
        if not resp:
            raise MDCResponseError('Empty response', resp)
        if resp[0] != HEADER_CODE:
            if (resp + self.reader._buffer) == b'MDCSTART<<TLS>>':
                raise MDCTLSRequired(resp + self.reader._buffer)
            raise MDCResponseError('Unexpected header',
                                   resp + self.reader._buffer)
        if resp[1] != RESPONSE_CMD:
            raise MDCResponseError('Unexpected cmd',
                                   resp + self.reader._buffer)
        if resp[2] != display_id:
            raise MDCResponseError('Unexpected display_id',
                                   resp + self.reader._buffer)

        length = resp[3]
        resp += await wait_for_read(self.reader, length + 1, self.timeout,
                                    'Response data read timeout')
        if self.verbose:
            self.verbose('Recv', repr_hex(resp))

        checksum = get_checksum(resp[1:-1])
        if checksum != int(resp[-1]):
            raise MDCResponseError('Checksum failed', resp)

        ack, rcmd, data = resp[4], resp[5], resp[6:-1]
        if ack not in (ACK_CODE, NAK_CODE):
            raise MDCResponseError('Unexpected ACK/NAK', resp)

        if subcmd and ack == ACK_CODE:
            # rsubcmd is not sent on NAK
            rsubcmd = data[0]
            data = data[1:]
        else:
            rsubcmd = None

        return (
            ack == ACK_CODE,
            (rcmd,) if rsubcmd is None else (rcmd, rsubcmd),
            data
        )

    async def close(self):
        if self.is_tls_started:
            # FIX warning
            # "returning true from eof_received() has no effect when using ssl"
            self.writer._protocol.eof_received = lambda: None
        writer = self.writer
        self.reader, self.writer = None, None
        writer.close()
        await wait_for(writer.wait_closed(), self.timeout, 'Close timeout')

    async def __aenter__(self):
        if not self.is_opened:
            await self.open()
        return self

    async def __aexit__(self, *args):
        if self.is_opened:
            await self.close()

    def __await__(self):
        return self.__aenter__().__await__()
