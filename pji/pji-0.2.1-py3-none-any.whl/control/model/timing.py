import io
import json
import math
import os
import re
from abc import ABCMeta
from typing import List, Tuple, Optional, Union, TypeVar, Type

from hbutils.model import get_repr_info

from ...utils import auto_encode_support, auto_decode_support, auto_load_json, JsonLoadError

_auto_encode = auto_encode_support(lambda x: x)
_auto_decode = auto_decode_support(lambda x: x)

_LINE_TYPING = Union[bytes, bytearray, str]
_TIMING_LINE_TYPING = Tuple[float, _LINE_TYPING]
_TIMING_LIST_TYPING = List[_TIMING_LINE_TYPING]


def _stable_process(lines: _TIMING_LIST_TYPING) -> _TIMING_LIST_TYPING:
    lines = [(float(_time), _auto_encode(_line).rstrip(b'\r\n')) for _time, _line in lines]
    _sorted = sorted([(_time, i, _line) for i, (_time, _line) in enumerate(lines)])
    return [(_time, _line) for _time, i, _line in _sorted]


class TimingContent(metaclass=ABCMeta):
    def __init__(self, lines: Optional[_TIMING_LIST_TYPING] = None):
        self.__lines = _stable_process(lines or [])

    @property
    def lines(self) -> List[Tuple[float, bytes]]:
        return list(self.__lines)

    @property
    def str_lines(self) -> List[Tuple[float, str]]:
        return [(_time, _auto_decode(_line)) for _time, _line in self.__lines]

    @classmethod
    def load(cls, stream) -> 'TimingContent':
        return _load_from_stream(stream, cls)

    @classmethod
    def loads(cls, data) -> 'TimingContent':
        return _load_from_data(data, cls)

    def to_json(self):
        return [{
            'time': _time,
            'line': _auto_decode(_line),
        } for _time, _line in self.__lines]

    __DUMP_FLOAT_LENGTH = 6

    def dumps(self) -> str:
        if self.__lines:
            _end_time = self.__lines[-1][0]
            _int_length = int(math.floor(math.log10(_end_time)) + 1)
            _mask = '%%.%sf' % self.__DUMP_FLOAT_LENGTH
            with io.StringIO() as s:
                for _time, _line in self.__lines:
                    _time_str = _mask % _time
                    _time_str = ' ' * (self.__DUMP_FLOAT_LENGTH + 1 + _int_length - len(_time_str)) + _time_str
                    s.write('[%s]%s%s' % (_time_str, _auto_decode(_line), _auto_decode(os.linesep)))

                return s.getvalue()
        else:
            return ''

    def dump(self, stream):
        _str_content = self.dumps()
        _bytes_content = _auto_encode(_str_content)
        try:
            stream.write(_bytes_content)
        except TypeError:
            stream.write(_str_content)

    def __eq__(self, other):
        if other is self:
            return True
        elif isinstance(other, TimingContent):
            return self.__lines == other.__lines
        else:
            return False

    def __repr__(self):
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('lines', lambda: len(self.__lines)),
                ('start_time', (lambda: '%.3fs' % self.__lines[0][0], lambda: len(self.__lines) > 0)),
                ('end_time', (lambda: '%.3fs' % self.__lines[-1][0], lambda: len(self.__lines) > 0)),
            ]
        )


_LINE_IDENT = (re.compile(r'\s*\[\s*(\d+(\.\d*)?)\s*]([\s\S]*)'), (1, 3))
_LINE_COMMENT = re.compile(r'\s*#\s*[\s\S]*')

_TS = TypeVar('_TS', bound=TimingContent)


def _load_from_line_ident(stream, cls: Type[_TS]) -> _TS:
    _result = []
    for line in stream:
        _str_line = _auto_decode(line).rstrip('\r\n')
        if _str_line.strip() and not _LINE_COMMENT.fullmatch(_str_line):
            _pattern, (_gtime, _gline) = _LINE_IDENT
            _match = _pattern.fullmatch(_str_line)
            if _match:
                _time, _line = float(_match[_gtime]), _auto_encode(_match[_gline])
                _result.append((_time, _line))
            else:
                raise ValueError('Invalid line {line} for timing script.'.format(line=repr(_str_line)))

    return cls(_result)


def _load_from_json(stream, cls: Type[_TS]) -> _TS:
    _json = auto_load_json(stream)
    if not isinstance(_json, list):
        raise TypeError('Timing script json should be a list but {actual} found.'.format(actual=type(_json).__name__))

    _result = []
    for _item in _json:
        if not isinstance(_item, dict):
            raise TypeError('Timing line should be a dict but {actual} found.'.format(actual=type(_item).__name__))

        _time = _item['time']
        try:
            _lines = _item['line']
        except KeyError:
            _lines = _item['lines']

        if isinstance(_lines, list):
            _lines = list(_lines)
        elif isinstance(_lines, dict):
            raise TypeError('Line should not be a dict.')
        else:
            _lines = [str(_lines)]

        for _line in _lines:
            _result.append((_time, _auto_encode(_line)))

    return cls(_result)


_METHODS = [
    (_load_from_line_ident, ValueError),
    (_load_from_json, (JsonLoadError, TypeError, KeyError))
]


def _load_from_stream(stream, cls: Type[_TS]) -> _TS:
    _init_position = stream.tell()
    _last_err = None

    for _func, _except in _METHODS:
        try:
            stream.seek(_init_position)
            return _func(stream, cls)
        except _except as err:
            _last_err = err

    raise _last_err


def _load_from_data(data, cls: Type[_TS]) -> _TS:
    if isinstance(data, cls):
        return data
    elif isinstance(data, list) or data is None:
        data = data or []
        if data and isinstance(data[0], tuple):
            return cls(data)
        else:
            with io.BytesIO(_auto_encode(json.dumps(data))) as b:
                return _load_from_json(b, cls)
    elif isinstance(data, str):
        with io.StringIO(data) as file:
            return cls.load(file)
    elif isinstance(data, (bytes, bytearray)):
        with io.BytesIO(bytes(data)) as file:
            return cls.load(file)
    else:
        raise TypeError('{cls}, list, str or bytes expected but {actual} found.'.format(
            cls=cls.__name__,
            actual=repr(type(data).__name__),
        ))
