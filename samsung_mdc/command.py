from functools import partial, partialmethod
from enum import Enum

from .exceptions import MDCResponseError, NAKError


class Field:
    def __init__(self, type, name=None, range=None):
        self.type, self.name, self.range = (
            type, name or type.__name__, range)

    def __call__(self, value):
        return self.type(value)


class CommandMcs(type):
    def __new__(mcs, name, bases, dict):
        if name.startswith('_') or name == 'Command':
            return type.__new__(mcs, name, bases, dict)

        if 'name' not in dict:
            dict['name'] = name.lower()

        if 'DATA' not in dict and bases:
            dict['DATA'] = bases[0].DATA
        dict['DATA'] = [
            x if isinstance(x, Field) else Field(x)
            for x in dict['DATA']
        ]
        if '__doc__' not in dict and bases and bases[0].__doc__:
            dict['__doc__'] = bases[0].__doc__

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
        # Allow command to be bounded as instance method
        return partial(self, connection)

    @staticmethod
    def parse_response(response):
        ack, rcmd, data = response
        if not ack:
            raise NAKError(data[0])
        return data

    @classmethod
    def parse_response_data(cls, data, strict_enum=True):
        rv = []
        for i, field in enumerate(cls.DATA):
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
        if len(data) != len(rv) and not cls.DATA[-1].type is str:
            raise MDCResponseError('Unexpected data length', data)
        return tuple(rv)

    @classmethod
    def pack_payload_data(cls, data):
        rv = bytes()
        for i, field in enumerate(cls.DATA):
            if field.type is str:
                rv += data[i].encode()
            else:
                rv += bytes((getattr(data[i], 'value', data[i]),))
        if len(data) != len(rv) and not cls.DATA[-1].type is str:
            raise ValueError('Unexpected data length')
        return rv

    @classmethod
    def get_order(cls):
        return (cls.CMD, cls.SUBCMD)
