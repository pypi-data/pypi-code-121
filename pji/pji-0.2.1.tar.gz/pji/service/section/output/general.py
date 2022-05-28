from enum import IntEnum, unique
from typing import Mapping, Any

from .base import FileOutputTemplate
from .copy import CopyFileOutputTemplate
from .tag import TagFileOutputTemplate


@unique
class FileOutputType(IntEnum):
    COPY = 1
    TAG = 2

    @classmethod
    def loads(cls, value) -> 'FileOutputType':
        """
        Load FileOutputType from value
        :param value: raw value
        :return: file output type object
        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            if value.upper() in cls.__members__.keys():
                return cls.__members__[value.upper()]
            else:
                raise KeyError('Unknown file output type - {actual}.'.format(actual=repr(value)))
        elif isinstance(value, int):
            _mapping = {v.value: v for k, v in cls.__members__.items()}
            if value in _mapping.keys():
                return _mapping[value]
            else:
                raise ValueError('Unknown file output type value - {actual}'.format(actual=repr(value)))
        else:
            raise TypeError('Int, str or {cls} expected but {actual} found.'.format(
                cls=cls.__name__,
                actual=repr(type(value).__name__)
            ))


_TYPE_TO_TEMPLATE_CLASS = {
    FileOutputType.COPY: CopyFileOutputTemplate,
    FileOutputType.TAG: TagFileOutputTemplate,
}


# noinspection DuplicatedCode
def _load_output_template_from_json(json: Mapping[str, Any]) -> FileOutputTemplate:
    """
    load template object from json data
    :param json: json data
    :return: file output template object
    """
    if 'type' not in json.keys():
        raise KeyError('Key {type} not found.'.format(type=repr('type')))

    _type = FileOutputType.loads(json['type'])
    _json = dict(json)
    del _json['type']

    return _TYPE_TO_TEMPLATE_CLASS[_type](**_json)


def _load_output_template_from_string(string: str) -> FileOutputTemplate:
    """
    load template object from string (should split with :)
    :param string: string value
    :return: file output template object
    """
    _items = string.split(':')
    _type, _args = FileOutputType.loads(_items[0].strip()), [_item.strip() for _item in _items[1:]]
    return _TYPE_TO_TEMPLATE_CLASS[_type](*_args)


def load_output_template(data) -> FileOutputTemplate:
    """
    load file output template object from data
    :param data: raw data
    :return: file output template object
    """
    if isinstance(data, FileOutputTemplate):
        return data
    elif isinstance(data, dict):
        return _load_output_template_from_json(data)
    elif isinstance(data, str):
        return _load_output_template_from_string(data)
    else:
        raise TypeError('Json, string or {type} expected but {actual} found.'.format(
            type=FileOutputTemplate.__name__, actual=repr(type(data).__name__)))
