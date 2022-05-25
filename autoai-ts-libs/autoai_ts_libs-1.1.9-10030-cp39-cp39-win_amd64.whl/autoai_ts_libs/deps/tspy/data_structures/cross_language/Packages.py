import abc

class Packages(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def java(self):
        pass

    @property
    @abc.abstractmethod
    def time_series(self):
        pass
