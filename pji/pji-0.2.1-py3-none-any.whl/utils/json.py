import json
from json import JSONDecodeError
from typing import Union

import yaml
from yaml.parser import ParserError as YamlParserError

_ERRORS_TYPING = Union[JSONDecodeError, YamlParserError]


class JsonLoadError(Exception):
    def __init__(self, exception: _ERRORS_TYPING):
        self.__exception = exception
        Exception.__init__(self, str(self.__exception))

    @property
    def exception(self) -> _ERRORS_TYPING:
        return self.__exception


_METHODS = [
    (json.load, JSONDecodeError),
    (yaml.safe_load, YamlParserError),
]


def auto_load_json(stream):
    _init_position = stream.tell()
    _last_err = None

    for _func, _except in _METHODS:
        try:
            stream.seek(_init_position)
            return _func(stream)
        except _except as err:
            _last_err = err

    raise JsonLoadError(_last_err)
