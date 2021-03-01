from typing import Union, Sequence, Tuple
from functools import partial
from enum import Enum
import asyncio


HEADER_CODE = 0xAA
RESPONSE_CMD = 0xFF
ACK_CODE = ord('A')  # 0x41 65
NAK_CODE = ord('N')  # 0x4E 78


def _repr_hex(value):
    # return ' '.join(f'{x:02x}:{x}' for x in value)
    return ' '.join(f'{x:02x}' for x in value)


class MDCError(Exception):
    pass


class MDCResponseError(MDCError):
    pass


class NAKError(MDCError):
    def __init__(self, error_code):
        self.error_code = error_code
        super().__init__(error_code)

    def __str__(self):
        return f'Negative Acknowledgement [error_code {self.error_code}]'


class MDCConnection:
    reader, writer = None, None

    def __init__(self, ip, port=1515, verbose=False):
        self.ip, self.port = ip, port
        self.verbose = verbose

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
                print(f'{self.ip}:{self.port}', 'Connected')

        self.writer.write(payload)
        if self.verbose:
            print(f'{self.ip}:{self.port}', 'Sent', _repr_hex(payload))
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
            print(f'{self.ip}:{self.port}', 'Recv', _repr_hex(resp))

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

    @staticmethod
    def parse_response(response):
        ack, rcmd, data = response
        if not ack:
            raise NAKError(data[0])
        return data

    @staticmethod
    def parse_response_data(data_format, data, strict_enum=True):
        rv = []
        for i, field in enumerate(data_format):
            if field.type is str:
                rv.append(data[i:].decode('utf8').rstrip('\x00'))
                break
            else:
                try:
                    value = field.type(data[i])
                except ValueError:
                    if not issubclass(field.type, Enum) or strict_enum:
                        raise
                    value = data[i]
                rv.append(value)
        if len(data) != len(rv) and not data_format[-1].type is str:
            raise MDCResponseError('Unexpected data length', data)
        return tuple(rv)

    @staticmethod
    def pack_payload_data(data_format, data):
        rv = bytes()
        for i, field in enumerate(data_format):
            if field.type is str:
                rv += data[i].encode()
            else:
                rv += bytes((getattr(data[i], 'value', data[i]),))
        if len(data) != len(rv) and not data_format[-1].type is str:
            raise ValueError('Unexpected data length')
        return rv

    _commands = {}

    @classmethod
    def register_command(cls, meta):
        pack_payload_data = getattr(
            meta, 'pack_payload_data',
            partial(cls.pack_payload_data, meta.DATA))
        parse_response_data = getattr(
            meta, 'parse_response_data',
            partial(cls.parse_response_data, meta.DATA))

        async def command(self, id, data):
            data = self.parse_response(
                await self.send(
                    (meta.CMD, meta.SUBCMD)
                    if hasattr(meta, 'SUBCMD') else meta.CMD,
                    id,
                    pack_payload_data(data) if data else []
                ),
            )
            return parse_response_data(data)
        if meta.GET:
            command.__defaults__ = (b'',)
        if not meta.SET or not meta.DATA:
            command = partial(command, data=b'')

        command.meta = meta
        cls._commands[meta.name] = command
        setattr(cls, meta.name, command)


from . import commands  # noqa # force commands to be registered
