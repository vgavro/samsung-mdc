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


def parse_videowall_model(value):
    """
    Splits coordinates byte (with y, x representation) to (x, y) tuple
    """
    return divmod(value, 1 << 4)[::-1]


def pack_videowall_model(value):
    """
    Converts (x, y) tuple to one coordinates byte (with y, x representation)
    """
    return [(value[1] * 16) + value[0]]
