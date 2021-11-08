from functools import partial, partialmethod
from enum import Enum

from .fields import Enum as EnumField
from .exceptions import MDCResponseError, NAKError


class CommandMcs(type):
    def __new__(mcs, name, bases, dict):
        if name.startswith('_') or name == 'Command':
            return type.__new__(mcs, name, bases, dict)

        if 'name' not in dict:
            dict['name'] = name.lower()

        if 'DATA' not in dict and bases:
            # allow naive DATA inheritance
            dict['DATA'] = bases[0].DATA
        if '__doc__' not in dict and bases and bases[0].__doc__:
            # doc is not inherited by default
            dict['__doc__'] = bases[0].__doc__

        dict['DATA'] = [
            # convert Enum to EnumField
            EnumField(x) if isinstance(x, type) and issubclass(x, Enum) else x
            for x in dict['DATA']
        ]
        dict['RESPONSE_DATA'] = [
            EnumField(x) if isinstance(x, type) and issubclass(x, Enum) else x
            for x in dict.get(
                'RESPONSE_DATA',
                dict['DATA'] + dict.get('RESPONSE_EXTRA', []))
        ]

        cls = type.__new__(mcs, name, bases, dict)

        if cls.GET:
            cls.__call__.__defaults__ = (b'',)
        if not cls.SET or not cls.DATA:
            cls.__call__ = partialmethod(cls.__call__, data=b'')

        return cls


class Command(metaclass=CommandMcs):
    CMD = None
    SUBCMD = None

    async def __call__(self, connection, display_id, data):
        data = self.parse_response(
            await connection.send(
                (self.CMD, self.SUBCMD)
                if self.SUBCMD is not None else self.CMD, display_id,
                self.pack_payload_data(data) if data else []
            ),
        )
        return self.parse_response_data(data)

    def __get__(self, connection, cls):
        # Allow Command to be bounded as instance method
        if connection is None:
            return self  # bind to class
        return partial(self, connection)  # bind to instance

    @staticmethod
    def parse_response(response):
        ack, rcmd, data = response
        if not ack:
            raise NAKError(data[0])
        return data

    @classmethod
    def parse_response_data(cls, data, strict_enum=True):
        rv, cursor = [], 0
        for field in cls.RESPONSE_DATA:
            if not field.parse_len:
                rv.append(field.parse(data[cursor:]))
                cursor = None
                break
            rv.append(field.parse(data[cursor:cursor + field.parse_len]))
            cursor += field.parse_len

        if cursor is not None and data[cursor:]:
            # Not consumed data left
            raise MDCResponseError('Unparsed data left', data[cursor:])
        return tuple(rv)

    @classmethod
    def pack_payload_data(cls, data):
        rv = bytes()
        for i, field in enumerate(cls.DATA):
            rv += bytes(field.pack(data[i]))
        if cls.DATA and len(data[i+1:]):
            raise ValueError('Unpacked data left '
                             '(more data provided than needed)')
        return rv

    @classmethod
    def get_order(cls):
        return (cls.CMD, cls.SUBCMD)
