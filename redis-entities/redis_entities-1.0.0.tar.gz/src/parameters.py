import datetime
import struct

def b2s(b):
    if isinstance(b, str):
        return b
    if not isinstance(b, bytes):
        raise TypeError("Invalid Bytes type")
    return b.decode("utf-8")


def require_string(a, int_to_string=False):
    if int_to_string and isinstance(a, int):
        a = str(a)
    if isinstance(a, bytes):
        a = b2s(a)
    if not isinstance(a, str):
        raise TypeError(f"A string object is required, not {str(type(a))}")
    return a


def b2timestamp(b):
    if not isinstance(b, bytes):
        raise TypeError("Invalid Bytes type")
    return struct.unpack(">L", b)[0]


def timestamp2b(timestamp):
    if isinstance(timestamp, bytes):
        return timestamp
    if isinstance(timestamp, datetime.datetime):
        timestamp = int(timestamp.timestamp())
    if isinstance(timestamp, float):
        timestamp = int(timestamp)
    if not isinstance(timestamp, int):
        raise TypeError("Invalid Timestamp Type")
    return struct.pack(">L", timestamp)


def require_timestamp_bytes(a):
    if isinstance(a, (int, datetime.datetime)):
        return timestamp2b(a)
    if not isinstance(a, bytes):
        raise TypeError(f"A byte object is required, not {str(type(a))}")
    return a


def s2b(s):
    if isinstance(s, bytes):
        return s
    if not isinstance(s, str):
        raise TypeError("Invalid String type")
    return s.encode("utf-8")


def require_bytes(a, int_to_string=False):
    if int_to_string and isinstance(a, int):
        a = str(a)
    if isinstance(a, str):
        return s2b(a)
    if not isinstance(a, bytes):
        raise TypeError(f"A byte object is required, not {str(type(a))}")
    return a