from enum import unique, IntEnum
from typing import Mapping

from .base import SectionInfoTemplate
from .local import LocalSectionInfoTemplate
from .static import StaticSectionInfoTemplate
from .tag import TagSectionInfoTemplate


@unique
class SectionInfoType(IntEnum):
    LOCAL = 1
    TAG = 2
    STATIC = 3

    @classmethod
    def loads(cls, value) -> 'SectionInfoType':
        """
        Load SectionInfoType from value
        :param value: raw value
        :return: info info type object
        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            if value.upper() in cls.__members__.keys():
                return cls.__members__[value.upper()]
            else:
                raise KeyError('Unknown info info type - {actual}.'.format(actual=repr(value)))
        elif isinstance(value, int):
            _mapping = {v.value: v for k, v in cls.__members__.items()}
            if value in _mapping.keys():
                return _mapping[value]
            else:
                raise ValueError('Unknown info info type value - {actual}'.format(actual=repr(value)))
        else:
            raise TypeError('Int, str or {cls} expected but {actual} found.'.format(
                cls=cls.__name__,
                actual=repr(type(value).__name__)
            ))


# noinspection DuplicatedCode
_TYPE_TO_TEMPLATE_CLASS = {
    SectionInfoType.LOCAL: LocalSectionInfoTemplate,
    SectionInfoType.TAG: TagSectionInfoTemplate,
    SectionInfoType.STATIC: StaticSectionInfoTemplate,
}


def _load_info_template_from_json(json: Mapping[str, str]) -> SectionInfoTemplate:
    """
    load template object from json data
    :param json: json data
    :return: info info template object
    """
    if 'type' not in json.keys():
        raise KeyError('Key {type} not found.'.format(type=repr('type')))

    _type = SectionInfoType.loads(json['type'])
    _json = dict(json)
    del _json['type']

    return _TYPE_TO_TEMPLATE_CLASS[_type](**_json)


def _load_info_template_from_string(string: str) -> SectionInfoTemplate:
    """
    load template object from string (should split with :)
    :param string: string value
    :return: file info template object
    """
    _items = string.split(':')
    _type, _args = SectionInfoType.loads(_items[0].strip()), [_item.strip() for _item in _items[1:]]
    return _TYPE_TO_TEMPLATE_CLASS[_type](*_args)


def load_info_template(data) -> SectionInfoTemplate:
    """
    load info info template object from data
    :param data: raw data
    :return: info info template object
    """
    if isinstance(data, SectionInfoTemplate):
        return data
    elif isinstance(data, dict):
        return _load_info_template_from_json(data)
    elif isinstance(data, str):
        return _load_info_template_from_string(data)
    else:
        raise TypeError('Json, string or {type} expected but {actual} found.'.format(
            type=SectionInfoTemplate.__name__, actual=repr(type(data).__name__)))
