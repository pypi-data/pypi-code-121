from abc import ABC, abstractmethod

__all__ = ["BasicSearchMethod"]


class BasicSearchMethod(ABC):
    """
    A basic class to search attacks
    """
    @abstractmethod
    def search(self, *args):
        pass
