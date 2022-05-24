# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import re
import struct
import threading

from enum import Enum as _Enum
from io import BytesIO


class Enum(_Enum):

    @classmethod
    def items(cls):

        return cls.to_dict().items()

    @classmethod
    def keys(cls):

        return cls.to_dict().keys()

    @classmethod
    def values(cls):

        return cls.to_dict().values()

    @classmethod
    def to_dict(cls):

        if not hasattr(cls, r'_to_dict'):
            setattr(cls, r'_to_dict', {item.name: item.value for item in cls})

        return getattr(cls, r'_to_dict')

    @classmethod
    def to_keys_dict(cls):

        if not hasattr(cls, r'_to_keys_dict'):
            setattr(cls, r'_to_keys_dict', {item.name: item for item in cls})

        return getattr(cls, r'_to_keys_dict')

    @classmethod
    def to_values_dict(cls):

        if not hasattr(cls, r'_to_values_dict'):
            setattr(cls, r'_to_values_dict', {item.value: item for item in cls})

        return getattr(cls, r'_to_values_dict')

    @classmethod
    def has_key(cls, key):

        return key in cls.to_keys_dict()

    @classmethod
    def has_value(cls, value):

        return value in cls.to_values_dict()


class Result(dict):
    """返回结果类
    """

    def __init__(self, code=0, **kwargs):

        super().__init__(code=code, **kwargs)

    def __bool__(self):

        return self.code == 0

    @property
    def code(self):

        return self.get(r'code')


class ThreadList(threading.local):
    """多线程安全的列表
    """

    __slots__ = [r'data']

    def __init__(self):

        self.data = []


class ThreadDict(threading.local):
    """多线程安全的字典
    """

    __slots__ = [r'data']

    def __init__(self):

        self.data = {}


class ByteArrayAbstract:
    """ByteArray抽象类
    """

    NETWORK = r'!'
    NATIVE = r'='
    NATIVE_ALIGNMENT = r'@'
    LITTLE_ENDIAN = r'<'
    BIG_ENDIAN = r'>'

    def __init__(self):

        self._endian = self.NETWORK

    def get_endian(self):

        return self._endian

    def set_endian(self, val):

        self._endian = val

    def read(self, size):

        raise NotImplementedError()

    def write(self, buffer):

        raise NotImplementedError()

    def read_pad_byte(self, _len):

        struct.unpack(f'{self._endian}{_len}x', self.read(_len))

    def write_pad_byte(self, _len):

        self.write(struct.pack(f'{self._endian}{_len}x'))

    def read_char(self):

        return struct.unpack(f'{self._endian}c', self.read(1))[0]

    def write_char(self, val):

        self.write(struct.pack(f'{self._endian}c', val))

    def read_signed_char(self):

        return struct.unpack(f'{self._endian}b', self.read(1))[0]

    def write_signed_char(self, val):

        self.write(struct.pack(f'{self._endian}b', val))

    def read_unsigned_char(self):

        return struct.unpack(f'{self._endian}B', self.read(1))[0]

    def write_unsigned_char(self, val):

        self.write(struct.pack(f'{self._endian}B', val))

    def read_bool(self):

        return struct.unpack(f'{self._endian}?', self.read(1))[0]

    def write_bool(self, val):

        self.write(struct.pack(f'{self._endian}?', val))

    def read_short(self):

        return struct.unpack(f'{self._endian}h', self.read(2))[0]

    def write_short(self, val):

        self.write(struct.pack(f'{self._endian}h', val))

    def read_unsigned_short(self):

        return struct.unpack(f'{self._endian}H', self.read(2))[0]

    def write_unsigned_short(self, val):

        self.write(struct.pack(f'{self._endian}H', val))

    def read_int(self):

        return struct.unpack(f'{self._endian}i', self.read(4))[0]

    def write_int(self, val):

        self.write(struct.pack(f'{self._endian}i', val))

    def read_unsigned_int(self):

        return struct.unpack(f'{self._endian}I', self.read(4))[0]

    def write_unsigned_int(self, val):

        self.write(struct.pack(f'{self._endian}I', val))

    def read_long(self):

        return struct.unpack(f'{self._endian}l', self.read(4))[0]

    def write_long(self, val):

        self.write(struct.pack(f'{self._endian}l', val))

    def read_unsigned_long(self):

        return struct.unpack(f'{self._endian}L', self.read(4))[0]

    def write_unsigned_long(self, val):

        self.write(struct.pack(f'{self._endian}L', val))

    def read_long_long(self):

        return struct.unpack(f'{self._endian}q', self.read(8))[0]

    def write_long_long(self, val):

        self.write(struct.pack(f'{self._endian}q', val))

    def read_unsigned_long_long(self):

        return struct.unpack(f'{self._endian}Q', self.read(8))[0]

    def write_unsigned_long_long(self, val):

        self.write(struct.pack(f'{self._endian}Q', val))

    def read_float(self):

        return struct.unpack(f'{self._endian}f', self.read(4))[0]

    def write_float(self, val):

        self.write(struct.pack(f'{self._endian}f', val))

    def read_double(self):

        return struct.unpack(f'{self._endian}d', self.read(8))[0]

    def write_double(self, val):

        self.write(struct.pack(f'{self._endian}d', val))

    def read_bytes(self, _len):

        return struct.unpack(f'{self._endian}{_len}s', self.read(_len))[0]

    def write_bytes(self, val):

        self.write(struct.pack(f'{self._endian}{len(val)}s', val))

    def read_string(self, _len):

        return self.read_bytes(_len).decode()

    def write_string(self, val):

        self.write_bytes(val.encode())

    def read_pascal_bytes(self, _len):

        return struct.unpack(f'{self._endian}{_len}p', self.read(_len))[0]

    def write_pascal_bytes(self, val):

        self.write(struct.pack(f'{self._endian}{len(val)}p', val))

    def read_pascal_string(self, _len):

        return self.read_pascal_bytes(_len).decode()

    def write_pascal_string(self, val):

        self.write_pascal_bytes(val.encode())

    def read_python_int(self, _len):

        return struct.unpack(f'{self._endian}{_len}P', self.read(_len))[0]

    def write_python_int(self, val):

        self.write(struct.pack(f'{self._endian}{len(val)}P', val))


class ByteArray(BytesIO, ByteArrayAbstract):
    """扩展的BytesIO类
    """

    NETWORK = r'!'
    NATIVE = r'='
    NATIVE_ALIGNMENT = r'@'
    LITTLE_ENDIAN = r'<'
    BIG_ENDIAN = r'>'

    def __init__(self, initial_bytes=None):

        BytesIO.__init__(self, initial_bytes)
        ByteArrayAbstract.__init__(self)


class KeyLowerDict(dict):

    _PATTERN = re.compile(r'(?<=[a-z])([A-Z])')

    def __init__(self, _dict):

        super().__init__(
            {
                KeyLowerDict._PATTERN.sub(r'_\1', key).lower(): KeyLowerDict(val) if isinstance(val, dict) else val
                for key, val in _dict.items()
            }
        )
