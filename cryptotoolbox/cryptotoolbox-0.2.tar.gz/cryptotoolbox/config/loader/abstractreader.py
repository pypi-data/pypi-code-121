__author__ = "hugo.inzirillo"

from abc import abstractmethod, ABCMeta


class AbstractYamlReader(metaclass=ABCMeta):

    @abstractmethod
    def _read(self, _path: str):
        """

        Returns
        -------

        """

        raise NotImplemented
