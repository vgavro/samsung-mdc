def bit_unmask(val, length=None):
    rv = tuple(reversed(tuple(int(x) for x in tuple('{0:0b}'.format(val)))))
    if length and len(rv) < length:
        return rv + ((0,) * (length - len(rv)))
    return rv
