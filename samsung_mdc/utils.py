from enum import Enum
from datetime import datetime


def _bit_unmask(val, length=None):
    rv = tuple(reversed(tuple(int(x) for x in tuple('{0:0b}'.format(val)))))
    if length and len(rv) < length:
        return rv + ((0,) * (length - len(rv)))
    return rv


def parse_enum_bitmask(enum, value):
    """
    Returns tuple of enum values, which was set to 1 in bitmask
    """
    return tuple(
        enum(i)
        for i, x in enumerate(
            _bit_unmask(value, length=len(enum)))
        if x
    )


def pack_bitmask(values):
    rv = 0
    for val in values:
        if isinstance(val, Enum):
            val = val.value
        rv |= (1 << val)
    return rv


def parse_mdc_time(day_part, hour, minute, second=0):
    """
    PM = 0x00
    AM = 0x01
    """
    return datetime.strptime(
        f'{day_part and "AM" or "PM"} {hour} {minute} {second}',
        '%p %I %M %S').time()


def pack_mdc_time(time):
    time = time.strftime('%p %I %M %S').split()
    return int(time[0] == 'AM'), int(time[1]), int(time[2]), int(time[3])


def repr_hex(value):
    # return ' '.join(f'{x:02x}/{x}' for x in value)
    return ':'.join(f'{x:02x}' for x in value)


def parse_hex(value):
    return value and bytes(int(x, 16) for x in value.split(':')) or b''


def parse_videowall(value):
    """
    Splits 8 byte 'coordinates' to 2x4 byte x/y/serial tuple
    The expected representation is Y, X
    """
    # Display returns as 2-bytes, coordinates and serial
    return divmod(value[0], 1<<4)[::-1] + (value[1], )


def pack_videowall(value):
    """
    Takes tuple of length 2 and combines its numbers as 2x4 to one 8 bit value
    Reverses representation to more intuitive X, Y
    """
    model = repr_hex(value)
    return model[4] + model[1] + model[-3:]
