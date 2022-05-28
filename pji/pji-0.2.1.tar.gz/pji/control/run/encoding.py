from ...utils import auto_decode_support, auto_encode_support

_auto_encode = auto_encode_support(lambda x: x)
_auto_decode = auto_decode_support(lambda x: x)


def _try_write(stream, data):
    _bytes_data = _auto_encode(data)
    _str_data = _auto_decode(_bytes_data)

    try:
        return stream.write(_bytes_data)
    except TypeError:
        return stream.write(_str_data)


def _try_read_to_bytes(stream):
    return _auto_encode(stream.read())
