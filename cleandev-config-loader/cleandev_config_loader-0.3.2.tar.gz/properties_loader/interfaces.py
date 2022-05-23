from abc import ABC
from abc import abstractmethod


class LoadConfig(ABC):

    @abstractmethod
    def __init__(self, root_path: str = None, path_file: str = None):
        raise NotImplemented

    @property
    @abstractmethod
    def path_properties(self) -> str:
        raise NotImplemented


class Properties(ABC):

    @abstractmethod
    def __init__(self, root_path: str = None, path_file: str = None):
        raise NotImplemented

    @property
    @abstractmethod
    def __dict__(self) -> dict:
        raise NotImplemented

