from abc import ABCMeta, abstractmethod


class FileOutputTemplate(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> 'FileOutput':
        raise NotImplementedError


class FileOutput(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, **kwargs):
        raise NotImplementedError
