from abc import ABCMeta
from typing import Mapping, Any, Optional, Callable

from .base import SectionInfoTemplate, SectionInfo
from .general import load_info_template
from ....utils import  wrap_empty
from hbutils.model import get_repr_info


class _ISectionInfoMapping(metaclass=ABCMeta):
    def __init__(self, items: Mapping[str, Any]):
        """
        :param items: mapping of section info objects
        """
        self.__items = items

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('keys', lambda: repr(tuple(sorted(self.__items.keys())))),
            ]
        )


class SectionInfoMappingTemplate(_ISectionInfoMapping):
    def __init__(self, **kwargs):
        """
        :param kwargs: mapping of section info template objects
        """
        self.__items = {key: load_info_template(data) for key, data in kwargs.items()}

        _ISectionInfoMapping.__init__(self, self.__items)

    @property
    def items(self) -> Mapping[str, SectionInfoTemplate]:
        return dict(self.__items)

    def __iter__(self):
        return self.items.items().__iter__()

    def __call__(self, **kwargs) -> 'SectionInfoMapping':
        """
        get section info info mapping object
        :param kwargs: plenty of arguments
        :return: section info info mapping object
        """
        return SectionInfoMapping(**{
            key: template(**kwargs) for key, template in self.__items.items()
        })

    @classmethod
    def loads(cls, data) -> 'SectionInfoMappingTemplate':
        """
        load section info mapping template from data
        :param data: raw data
        :return: section info mapping template
        """
        data = data or {}
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise TypeError('Json or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


_INFO_MAPPING_RESULT = Mapping[str, Any]


class SectionInfoMapping(_ISectionInfoMapping):
    def __init__(self, **kwargs):
        """
        :param kwargs: mapping of section info objects
        """
        self.__items = kwargs

        _ISectionInfoMapping.__init__(self, self.__items)

    @property
    def items(self) -> Mapping[str, SectionInfo]:
        return dict(self.__items)

    def __iter__(self):
        return self.items.items().__iter__()

    def __call__(self, info_mapping_start: Optional[Callable[['SectionInfoMapping'], None]] = None,
                 info_mapping_complete: Optional[Callable[['SectionInfoMapping', _INFO_MAPPING_RESULT], None]] = None,
                 **kwargs) -> _INFO_MAPPING_RESULT:
        """
        execute this info info
        """
        wrap_empty(info_mapping_start)(self)
        _ret = {key: info() for key, info in self.__items.items()}
        _result = {key: _data for key, (_ok, _data) in _ret.items() if _ok}

        wrap_empty(info_mapping_complete)(self, _result)
        return _result
