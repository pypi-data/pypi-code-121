from abc import ABCMeta, abstractmethod


class SectionInfoTemplate(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> 'SectionInfo':
        raise NotImplementedError


class SectionInfo(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, **kwargs):
        raise NotImplementedError
