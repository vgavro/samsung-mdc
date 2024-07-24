from typing import Sequence
from datetime import datetime, time

from .utils import (
    parse_mdc_time, pack_mdc_time, parse_enum_bitmask, pack_bitmask,
    pack_videowall_model, parse_videowall_model)


class Field:
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.upper()

    def parse(self, data):
        # returns data and cursor shift
        return data, len(data)

    def pack(self, value):
        return [value]


class Int(Field):
    range = None

    def __init__(self, name=None, range=None, length=1, byteorder='big'):
        super().__init__(name)
        self.range = range
        self.length = length
        self.byteorder = byteorder

    def pack(self, value):
        if self.range and value not in self.range:
            raise ValueError('Field not in range', self.name, self.range)
        return int(value).to_bytes(self.length, byteorder=self.byteorder)

    def parse(self, data):
        return int.from_bytes(data[:self.length], self.byteorder), self.length


class Bool(Int):
    range = range(2)

    def parse(self, data):
        return bool(data[0]), 1


class Enum(Field):
    def __init__(self, enum, name=None):
        self.enum = enum
        super().__init__(name or enum.__name__)

    def parse(self, data):
        return self.enum(data[0]), 1

    def pack(self, value):
        if isinstance(value, str):
            value = self.enum[value]
        return [self.enum(value).value]


class Str(Field):
    def __init__(self, name=None, length=None):
        self.length = length
        super().__init__(name)

    def parse(self, data):
        length = self.length or len(data)
        return data[:length].decode('utf8').rstrip('\x00'), length

    def pack(self, value):
        if self.length is not None and len(value) > self.length:
            raise ValueError('Field length exceeded', len(value), self.length)
        return value.encode('utf8')


class StrCoded(Field):
    def __init__(self, code, name=None):
        super().__init__(name)
        self.code = code

    def parse(self, data):
        if self.code != data[0]:
            raise ValueError('Expected code not matched', data[0])
        length = data[1]
        if not length:
            return '', 2
        return data[2:length + 2].decode('utf8'), length + 2

    def pack(self, value):
        encoded = value.encode('utf8')
        return bytes([self.code, len(encoded)]) + encoded


class Time12H(Field):
    def parse(self, data):
        return parse_mdc_time(data[2], data[0], data[1]), 3

    def pack(self, data):
        day_part, hour, minute, second = pack_mdc_time(data)
        return (hour, minute, day_part)


class Time(Field):
    def __init__(self, name=None, seconds=False):
        self.seconds = seconds
        super().__init__(name)

    def parse(self, data):
        return (
            time(data[0], data[1], data[3] if self.seconds else 0),
            3 if self.seconds else 2
        )

    def pack(self, data):
        if self.seconds:
            return (data.hour, data.minute, data.second)
        return (data.hour, data.minute)


class DateTime(Field):
    name = 'datetime'

    def __init__(self, name=None, seconds=True):
        self.seconds = seconds
        super().__init__(name)

    def parse(self, data):
        if self.seconds:
            time = parse_mdc_time(data[7], data[1], data[2], data[3])
            return datetime(
                int.from_bytes(data[5:7], 'big'),  # year
                data[4], data[0],  # month, day
                time.hour, time.minute, time.second
            ), 8

        time = parse_mdc_time(data[6], data[1], data[2])
        return datetime(
                int.from_bytes(data[4:6], 'big'),  # year
                data[3], data[0],  # month, day
                time.hour, time.minute, time.second
        ), 7

    def pack(self, value):
        day_part, hour, minute, second = pack_mdc_time(value.time())
        return (
            bytes([value.day, hour, minute])
            + (self.seconds and bytes([second]) or b'')
            + bytes([value.month])
            + int.to_bytes(value.year, 2, 'big') + bytes([day_part]))


class Bitmask(Enum):
    def parse(self, data):
        return parse_enum_bitmask(self.enum, data[0]), 1

    def pack(self, data):
        if not isinstance(data, Sequence):
            raise ValueError('Bitmask values must be sequence')
        return [pack_bitmask(data)]


class IPAddress(Field):
    def parse(self, data):
        return '.'.join(str(int(x)) for x in data[:4]), 4

    def pack(self, data):
        rv = tuple(int(x) for x in data.split('.'))
        if not len(rv) == 4 or not all(0 <= x < 256 for x in rv):
            raise ValueError('Invalid IP address', data)
        return rv


class VideoWallModel(Field):
    def parse(self, data):
        return parse_videowall_model(data[0]), 1

    def pack(self, data):
        if isinstance(data, str):
            rv = tuple(int(x) for x in data.split(','))
        elif not isinstance(data, (tuple, list)):
            raise TypeError('Video wall model must be Tuple[int, int] or'
                            'comma-separated string')
        if not len(rv) == 2:
            raise ValueError('Invalid video wall model', data)
        return pack_videowall_model(rv)
