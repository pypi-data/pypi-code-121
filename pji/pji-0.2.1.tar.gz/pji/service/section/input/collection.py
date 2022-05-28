from abc import ABCMeta
from typing import List, Optional, Callable

from hbutils.model import get_repr_info

from .base import FileInputTemplate, FileInput
from .general import load_input_template
from ....utils import wrap_empty


class _IFileInputCollection(metaclass=ABCMeta):
    def __init__(self, items):
        """
        :param items: file inputs
        """
        self.__items = items

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('inputs', lambda: len(self.__items)),
            ]
        )


class FileInputCollectionTemplate(_IFileInputCollection):
    def __init__(self, *items):
        """
        :param items: file input templates
        """
        self.__items = [load_input_template(item) for item in items]
        _IFileInputCollection.__init__(self, self.__items)

    @property
    def items(self) -> List[FileInputTemplate]:
        return list(self.__items)

    def __iter__(self):
        return self.items.__iter__()

    def __call__(self, **kwargs) -> 'FileInputCollection':
        """
        generate file input collection
        :param kwargs: plenty of arguments
        :return: file input collection
        """
        return FileInputCollection(*[item(**kwargs) for item in self.__items])

    @classmethod
    def loads(cls, data) -> 'FileInputCollectionTemplate':
        """
        load file input collection template from data
        :param data: raw data
        :return: file input collection template
        """
        data = data or []
        if isinstance(data, cls):
            return data
        elif isinstance(data, FileInputTemplate):
            return cls(data)
        elif isinstance(data, (list, tuple)):
            return cls(*data)
        elif isinstance(data, (dict, str)):
            return cls(load_input_template(data))
        else:
            raise TypeError('Array or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


class FileInputCollection(_IFileInputCollection):
    def __init__(self, *items):
        """
        :param items: file inputs
        """
        self.__items = items
        _IFileInputCollection.__init__(self, self.__items)

    @property
    def items(self) -> List[FileInput]:
        return list(self.__items)

    def __iter__(self):
        return self.items.__iter__()

    def __call__(self, input_collection_start: Optional[Callable[['FileInputCollection'], None]] = None,
                 input_collection_complete: Optional[Callable[['FileInputCollection'], None]] = None, **kwargs):
        """
        execute this file input setting
        """
        wrap_empty(input_collection_start)(self)
        for item in self.__items:
            item(**kwargs)
        wrap_empty(input_collection_complete)(self)
