# Generic CBOR encoder / decoder

# Copyright (c) 2022 Steffen Kieß

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# https://datatracker.ietf.org/doc/html/rfc8949

import collections.abc
import dataclasses
import enum
import io
import struct

__all__ = ('SimpleValue', 'false', 'true', 'null', 'undefined', 'Type',
           'get_type', 'Map', 'Tag', 'Decoder', 'default_decoder', 'Encoder',
           'default_encoder', 'decode', 'encode')


@dataclasses.dataclass(frozen=True)
class SimpleValue:
    value: int

    def __init__(self, value: int, /):
        if not isinstance(value, int):
            raise ValueError('value is not an int value')
        value = int(value)
        if value < 0 or value > 255:
            raise ValueError('value is out of range')
        if value >= 24 and value < 32:
            raise ValueError('reserved value')
        object.__setattr__(self, 'value', value)

    def __repr__(self):
        if self.value == 20:
            return 'false'
        elif self.value == 21:
            return 'true'
        elif self.value == 22:
            return 'null'
        elif self.value == 23:
            return 'undefined'
        return 'SimpleValue({})'.format(self.value)


false = SimpleValue(20)
true = SimpleValue(21)
null = SimpleValue(22)
undefined = SimpleValue(23)


class Type(enum.Enum):
    # https://datatracker.ietf.org/doc/html/rfc8949#section-2
    INTEGER = 1
    SIMPLE_VALUE = 2
    FLOAT = 3
    BYTE_STRING = 4
    TEXT_STRING = 5
    ARRAY = 6
    MAP = 7
    TAG = 8


def get_type(value):
    if isinstance(value, int) and not isinstance(value, bool):
        return Type.INTEGER
    elif isinstance(value, SimpleValue) or isinstance(value, bool) \
            or value is None:
        return Type.SIMPLE_VALUE
    elif isinstance(value, float):
        return Type.FLOAT
    elif isinstance(value, bytes):
        return Type.BYTE_STRING
    elif isinstance(value, str):
        return Type.TEXT_STRING
    elif isinstance(value, tuple) and not isinstance(value, Tag) \
            and not isinstance(value, SimpleValue) or isinstance(value, list):
        return Type.ARRAY
    elif isinstance(value, Map) or isinstance(value, dict):
        return Type.MAP
    elif isinstance(value, Tag):
        return Type.TAG
    else:
        raise ValueError('Got value with unknown type: {}'.format(type(value)))


def get_value(value, /, decode_simple=True):
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    elif isinstance(value, SimpleValue):
        if decode_simple:
            if value == false:
                return False
            if value == true:
                return True
            if value == null:
                return None
        return value
    elif isinstance(value, bool) or value is None:
        if decode_simple:
            return value
        else:
            if value is None:
                return null
            elif value is False:
                return false
            elif value is True:
                return true
            else:
                raise Exception('Unknown bool/None value')
    elif isinstance(value, bool) or value is None:
        return Type.SIMPLE_VALUE
    elif isinstance(value, float):
        return value
    elif isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value
    # TODO: Should get_value be called recursively?
    elif isinstance(value, tuple) and not isinstance(value, Tag) \
            and not isinstance(value, SimpleValue):
        return value
    elif isinstance(value, Map):
        return value
    elif isinstance(value, Tag):
        return value
    else:
        raise ValueError('Got value with unknown type: {}'.format(type(value)))


class Map(collections.abc.Mapping):
    __slots__ = ('__d', '__hash', '__decode_simple')

    def __init__(self, arg={}, /, decode_simple=None):
        self.__d = {}
        self.__hash = None

        if decode_simple is None:
            if hasattr(arg, 'decode_simple'):
                decode_simple = arg.decode_simple
            else:
                decode_simple = True

        if not isinstance(decode_simple, bool):
            raise ValueError('decode_simple is not a boolean value')
        self.__decode_simple = decode_simple

        if hasattr(arg, 'keys'):
            for key in arg:
                key = get_value(key, decode_simple=decode_simple)
                new_key = (get_type(key), key)
                if new_key in self.__d:
                    raise DuplicateKeyInMapError()
                value = arg[key]
                value = get_value(value, decode_simple=decode_simple)
                self.__d[new_key] = value
        else:
            for key, value in arg:
                key = get_value(key, decode_simple=decode_simple)
                value = get_value(value, decode_simple=decode_simple)
                new_key = (get_type(key), key)
                if new_key in self.__d:
                    raise DuplicateKeyInMapError()
                self.__d[new_key] = value

    @property
    def decode_simple(self):
        """
        Whether to decode simple values 20-22 into False / True / None.
        """
        return self.__decode_simple

    def __iter__(self):
        for _type, key in self.__d:
            yield key

    def __len__(self):
        return len(self.__d)

    def __getitem__(self, key):
        new_key = (get_type(key), key)
        return self.__d[new_key]

    def __repr__(self):
        return "%s({%s}%s)" % (self.__class__.__name__, ', '.join([
            '{!r}: {!r}'.format(key, self[key]) for key in self
        ]), '' if self.decode_simple else ', decode_simple=False')

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((frozenset(self), frozenset(self.values())))
        return self._hash


@dataclasses.dataclass(frozen=True)
class Tag:
    number: int
    content: object

    def __init__(self, number, content):
        if not isinstance(number, int):
            raise ValueError('number is not an int value')
        number = int(number)
        if number < 0 or number >= 2**64:
            raise ValueError('number is out of range')
        object.__setattr__(self, 'number', number)
        object.__setattr__(self, 'content', content)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.number, self.content)


class EndMarkerType():
    __slots__ = ()


class EOFType():
    __slots__ = ()


end_marker = EndMarkerType()
eof = EOFType()


class DecodeError(Exception):
    pass


class GotDataAfterEndError(DecodeError):
    pass


class MaximumNestingDepthExceededError(DecodeError):
    pass


class NotWellFormedError(DecodeError):
    __slots__ = ()

    def __init__(self, msg=None):
        if msg is None:
            msg = type(self).__name__
        super(NotWellFormedError, self).__init__(
            'CBOR document not well-formed: {})'.format(msg))


class UnexpectedEOFError(NotWellFormedError):
    pass


class InvalidAdditionalValueError(NotWellFormedError):
    __slots__ = ('major_type', 'additional', 'allow_end_marker')

    def __init__(self, major_type, additional, allow_end_marker):
        self.major_type = major_type
        self.additional = additional
        self.allow_end_marker = allow_end_marker
        super(InvalidAdditionalValueError, self).__init__(
            'Invalid additional value {} for major type {} (end markers {})'
            .format(self.additional, self.major_type,
                    'allowed' if self.allow_end_marker else 'not allowed'))


class InvalidSimpleValueError(NotWellFormedError):
    __slots__ = ('major_type', 'additional', 'allow_end_marker')

    def __init__(self, argument):
        self.argument = argument
        super(InvalidSimpleValueError, self).__init__(
            'got major code 7 with additional 24 and argument {}'
            .format(self.argument))


class NotValidError(DecodeError):
    __slots__ = ()

    def __init__(self, msg=None):
        if msg is None:
            msg = type(self).__name__
        super(NotValidError, self).__init__(
            'CBOR document not valid: {})'.format(msg))


class NotBasicValidError(NotValidError):
    def __init__(self, msg=None):
        super(NotBasicValidError, self).__init__(msg)


class DuplicateKeyInMapError(NotBasicValidError):
    pass


class NotValidUTF8StringError(NotBasicValidError):
    def __init__(self, msg):
        super(NotBasicValidError, self).__init__(
            'could not decode utf-8 string' + msg)


class Decoder:
    __slots__ = ('__decode_simple')

    def __init__(self, *, decode_simple=True):
        if not isinstance(decode_simple, bool):
            raise ValueError('decode_simple is not a boolean value')
        self.__decode_simple = decode_simple

    @property
    def decode_simple(self):
        """
        Whether to decode simple values 20-22 into False / True / None.
        """
        return self.__decode_simple

    def _read_byte(self, fp, *, allow_eof=False):
        byte = fp.read(1)
        if not isinstance(byte, bytes):
            raise ValueError(
                'Got a {} instead of a bytes value when reading data'
                .format(type(byte)))
        if len(byte) == 0:
            if not allow_eof:
                raise UnexpectedEOFError()
            else:
                return None
        if len(byte) != 1:
            raise ValueError('Expected 1 byte, got {} bytes'.format(len(byte)))
        return byte[0]

    def _read_bytes(self, fp, count):
        data = fp.read(count)
        if not isinstance(data, bytes):
            raise ValueError(
                'Got a {} instead of a bytes value when reading data'
                .format(type(data)))
        if len(data) < count:
            raise UnexpectedEOFError()
        if len(data) != count:
            raise ValueError(
                'Expected {} bytes, got {} bytes'.format(count, len(data)))
        return data

    def _read_major_and_argument(self, fp, /, allow_end_marker,
                                 allow_eof=False):
        initial_byte = self._read_byte(fp, allow_eof=allow_eof)
        if initial_byte is None:
            return eof, None, None
        major_type = initial_byte >> 5
        additional = initial_byte & 31

        if additional < 24:
            argument = additional
        elif additional == 24:
            argument = self._read_byte(fp)
        elif additional == 25:
            argument = struct.unpack('>H', self._read_bytes(fp, 2))[0]
        elif additional == 26:
            argument = struct.unpack('>L', self._read_bytes(fp, 4))[0]
        elif additional == 27:
            argument = struct.unpack('>Q', self._read_bytes(fp, 8))[0]
        elif additional == 31 and major_type in (2, 3, 4, 5):
            argument = None
        elif additional == 31 and major_type == 7 and allow_end_marker:
            return end_marker, None, additional
        else:
            raise InvalidAdditionalValueError(
                major_type, additional, allow_end_marker)

        return major_type, argument, additional

    def read(self, fp, /, *, allow_end_marker=False, allow_eof=False,
             max_depth=None):
        # https://datatracker.ietf.org/doc/html/rfc8949#section-3

        if max_depth is not None:
            if max_depth < 0:
                raise MaximumNestingDepthExceededError()
            max_depth = max_depth - 1

        major_type, argument, additional = \
            self._read_major_and_argument(fp, allow_end_marker, allow_eof)
        if major_type in (end_marker, eof):
            return major_type

        # https://datatracker.ietf.org/doc/html/rfc8949#section-3.1
        if major_type == 0:  # unsigned integer
            return argument
        elif major_type == 1:  # negative integer
            return - 1 - argument
        elif major_type == 2:  # byte string
            if argument is not None:  # not indefinite length
                return self._read_bytes(fp, argument)
            else:  # indefinite length
                res = bytearray()
                while True:
                    sub_major_type, sub_argument, sub_additional = \
                        self._read_major_and_argument(fp, True)
                    if sub_major_type is end_marker:
                        return bytes(res)
                    if sub_major_type != major_type:
                        raise NotWellFormedError(
                          'got non-bytestring in indefinite length bytestring')
                    if sub_argument is None:
                        raise NotWellFormedError(
                            'got nested indefinite length bytestring')
                    res += self._read_bytes(fp, sub_argument)
        elif major_type == 3:  # string
            if argument is not None:  # not indefinite length
                try:
                    return self._read_bytes(fp, argument).decode('utf-8')
                except UnicodeDecodeError as e:
                    raise NotValidUTF8StringError(str(e))
            else:  # indefinite length
                res = []
                while True:
                    sub_major_type, sub_argument, sub_additional = \
                        self._read_major_and_argument(fp, True)
                    if sub_major_type is end_marker:
                        return ''.join(res)
                    if sub_major_type != major_type:
                        raise NotWellFormedError(
                            'got non-string in indefinite length string')
                    if sub_argument is None:
                        raise NotWellFormedError(
                            'got nested indefinite length string')
                    try:
                        res.append(self._read_bytes(
                            fp, sub_argument).decode('utf-8'))
                    except UnicodeDecodeError as e:
                        raise NotValidUTF8StringError(str(e))
        elif major_type == 4:  # array
            if argument is not None:  # not indefinite length
                res = []
                for i in range(argument):
                    res.append(self.read(fp, max_depth=max_depth))
                return tuple(res)
            else:  # indefinite length
                res = []
                while True:
                    value = self.read(fp, max_depth=max_depth,
                                      allow_end_marker=True)
                    if value is end_marker:
                        return tuple(res)
                    res.append(value)
        elif major_type == 5:  # map
            if argument is not None:  # not indefinite length
                res = []
                for i in range(argument):
                    key = self.read(fp, max_depth=max_depth)
                    value = self.read(fp, max_depth=max_depth)
                    res.append((key, value))
                return Map(res)
            else:  # indefinite length
                res = []
                while True:
                    key = self.read(fp, max_depth=max_depth,
                                    allow_end_marker=True)
                    if key is end_marker:
                        return Map(res)
                    value = self.read(fp, max_depth=max_depth)
                    res.append((key, value))
        elif major_type == 6:  # tag
            content = self.read(fp, max_depth=max_depth)
            return Tag(argument, content)
        elif major_type == 7:  # simple values and floating point numbers
            # https://datatracker.ietf.org/doc/html/rfc8949#section-3.3
            if additional < 24:
                return get_value(SimpleValue(argument),
                                 decode_simple=self.decode_simple)
            elif additional == 24:
                if argument < 32:
                    raise InvalidSimpleValueError(argument)
                return get_value(SimpleValue(argument),
                                 decode_simple=self.decode_simple)
            # TODO: Should nan values which only differ in the sign be
            # considered the same?
            # https://datatracker.ietf.org/doc/html/rfc8949#section-5.6.1
            elif additional == 25:
                return struct.unpack('>e', struct.pack('>H', argument))[0]
            elif additional == 26:
                return struct.unpack('>f', struct.pack('>I', argument))[0]
            elif additional == 27:
                return struct.unpack('>d', struct.pack('>Q', argument))[0]
            else:
                raise Exception('Invalid major_type 7 argument')
        else:
            raise Exception('Invalid major_type')

        raise Exception('Should not be reached')


default_decoder = Decoder()


class Encoder:
    __slots__ = ()

    def __init__(self):
        pass

    def _write_byte(self, fp, value):
        if not isinstance(value, int):
            raise Exception('not isinstance(value, int)')
        if value < 0 or value > 255:
            raise Exception('value < 0 or value > 255')
        fp.write(bytes([value]))

    def _encode_argument(self, fp, major_type, argument):
        if major_type < 0 or major_type > 7:
            raise Exception('major_type < 0 or major_type > 7')
        if argument < 0 or argument >= 2**64:
            raise Exception('argument < 0 or argument >= 2**64')

        if argument < 24:
            self._write_byte(fp, major_type << 5 | argument)
        elif argument < 2 ** 8:
            self._write_byte(fp, major_type << 5 | 24)
            self._write_byte(fp, argument)
        elif argument < 2 ** 16:
            self._write_byte(fp, major_type << 5 | 25)
            fp.write(struct.pack('>H', argument))
        elif argument < 2 ** 32:
            self._write_byte(fp, major_type << 5 | 26)
            fp.write(struct.pack('>L', argument))
        elif argument < 2 ** 64:
            self._write_byte(fp, major_type << 5 | 27)
            fp.write(struct.pack('>Q', argument))

    def write(self, fp, value, /, *, max_depth=None):
        if max_depth is not None:
            if max_depth < 0:
                raise MaximumNestingDepthExceededError()
            max_depth = max_depth - 1

        ty = get_type(value)

        if ty == Type.INTEGER:
            value = int(value)
            if value < 0:
                abs_value = -value - 1
                major_type = 1
            else:
                abs_value = value
                major_type = 0
            if abs_value >= 2**64:
                raise ValueError('Integer value {} overflows'.format(value))
            self._encode_argument(fp, major_type, abs_value)
        elif ty == Type.SIMPLE_VALUE:
            val = int(get_value(value, decode_simple=False).value)
            if val < 0 or val > 255:
                raise Exception('val < 0 or val > 255')
            if val < 24:
                self._write_byte(fp, 7 << 5 | val)
            else:
                self._write_byte(fp, 7 << 5 | 24)
                self._write_byte(fp, val)
        elif ty == Type.FLOAT:
            # TODO: Different nan values are not preserved by struct.pack
            value = float(value)
            enc64 = struct.pack('>d', value)
            try:
                enc16 = struct.pack('>e', value)
            except OverflowError:
                enc16 = b'\x00\x00'
            val16 = struct.pack('>d', struct.unpack('>e', enc16)[0])
            if val16 == enc64:
                self._write_byte(fp, 7 << 5 | 25)
                fp.write(enc16)
            else:
                try:
                    enc32 = struct.pack('>f', value)
                except OverflowError:
                    enc32 = b'\x00\x00\x00\x00'
                val32 = struct.pack('>d', struct.unpack('>f', enc32)[0])
                if val32 == enc64:
                    self._write_byte(fp, 7 << 5 | 26)
                    fp.write(enc32)
                else:
                    self._write_byte(fp, 7 << 5 | 27)
                    fp.write(enc64)
        elif ty == Type.BYTE_STRING:
            value = bytes(value)
            self._encode_argument(fp, 2, len(value))
            fp.write(value)
        elif ty == Type.TEXT_STRING:
            value_b = bytes(value, 'utf-8')
            self._encode_argument(fp, 3, len(value_b))
            fp.write(value_b)
        elif ty == Type.ARRAY:
            value = tuple(value)
            self._encode_argument(fp, 4, len(value))
            for val in value:
                self.write(fp, val, max_depth=max_depth)
        elif ty == Type.MAP:
            # https://datatracker.ietf.org/doc/html/rfc8949#section-4.2.1

            keys = []
            for key in value:
                b = io.BytesIO()
                self.write(b, key, max_depth=max_depth)
                encoded_key = b.getvalue()
                keys.append((encoded_key, key))
            keys.sort(key=lambda v: v[0])

            # TODO: Support "Length-First Map Key Ordering"?
            # https://datatracker.ietf.org/doc/html/rfc8949#section-4.2.3
            self._encode_argument(fp, 5, len(keys))

            last_key = None
            for encoded_key, key in keys:
                # Note that duplicate keys should be directly after each other
                # because the array is sorted
                if encoded_key == last_key:
                    # Should never happen because Map/dict should prevent
                    # duplicates.
                    # TODO: dict won't prevent e.g. duplicates with `null` and
                    # `None`: `gencbor.encode({None:1, gencbor.null:2})`
                    raise Exception('Encountered duplicate key')
                fp.write(encoded_key)
                self.write(fp, value[key], max_depth=max_depth)
                last_key = encoded_key
        elif ty == Type.TAG:
            self._encode_argument(fp, 6, value.number)
            self.write(fp, value.content, max_depth=max_depth)
        else:
            raise Exception('Invalid type: {}'.format(ty))


default_encoder = Encoder()


def decode(b: bytes, /, max_depth=None):
    if not isinstance(b, bytes):
        raise ValueError('value is not a byte string')
    fp = io.BytesIO(b)
    result = default_decoder.read(fp, max_depth=max_depth)
    if len(fp.read(1)) != 0:
        raise GotDataAfterEndError()
    return result


def encode(value, /, max_depth=None):
    fp = io.BytesIO()
    result = default_encoder.write(fp, value, max_depth=max_depth)
    return fp.getvalue()
