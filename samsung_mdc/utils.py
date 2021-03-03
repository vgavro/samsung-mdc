from datetime import datetime


def bit_unmask(val, length=None):
    rv = tuple(reversed(tuple(int(x) for x in tuple('{0:0b}'.format(val)))))
    if length and len(rv) < length:
        return rv + ((0,) * (length - len(rv)))
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
