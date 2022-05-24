from abc import ABC
from abc import abstractmethod


class BaseStub(ABC):
    """Base stub class that enforces a close() implementation."""

    @abstractmethod
    def close(self):
        pass
