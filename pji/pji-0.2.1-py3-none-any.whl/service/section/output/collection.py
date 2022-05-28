from typing import List, Optional, Callable

from hbutils.model import get_repr_info

from .base import FileOutputTemplate, FileOutput
from .general import load_output_template
from ....utils import wrap_empty


class _IFileOutputCollection:
    def __init__(self, items):
        """
        :param items: file outputs
        """
        self.__items = items

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('outputs', lambda: len(self.__items)),
            ]
        )


class FileOutputCollectionTemplate(_IFileOutputCollection):
    def __init__(self, *items):
        """
        :param items: file output templates
        """
        self.__items = [load_output_template(item) for item in items]
        _IFileOutputCollection.__init__(self, self.__items)

    @property
    def items(self) -> List[FileOutputTemplate]:
        return list(self.__items)

    def __iter__(self):
        return self.items.__iter__()

    def __call__(self, **kwargs):
        """
        generate file output collection
        :param kwargs: plenty of arguments
        :return: file output collection
        """
        return FileOutputCollection(*[item(**kwargs) for item in self.__items])

    @classmethod
    def loads(cls, data) -> 'FileOutputCollectionTemplate':
        """
        load file output collection template from data
        :param data: raw data
        :return: file output collection template
        """
        data = data or []
        if isinstance(data, cls):
            return data
        elif isinstance(data, FileOutputTemplate):
            return cls(data)
        elif isinstance(data, (list, tuple)):
            return cls(*data)
        elif isinstance(data, (dict, str)):
            return cls(load_output_template(data))
        else:
            raise TypeError('Array or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


class FileOutputCollection(_IFileOutputCollection):
    def __init__(self, *items):
        """
        :param items: file outputs
        """
        self.__items = list(items)
        _IFileOutputCollection.__init__(self, self.__items)

    @property
    def items(self) -> List[FileOutput]:
        return list(self.__items)

    def __iter__(self):
        return self.items.__iter__()

    def __call__(self, output_collection_start: Optional[Callable[['FileOutputCollection'], None]] = None,
                 output_collection_complete: Optional[Callable[['FileOutputCollection'], None]] = None, **kwargs):
        """
        execute this file output setting
        """
        wrap_empty(output_collection_start)(self)
        for item in self.__items:
            item(**kwargs)
        wrap_empty(output_collection_complete)(self)
