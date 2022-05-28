from abc import ABC, abstractmethod

__all__ = ["BasicTransformation"]


class BasicTransformation(ABC):
    """
    A basic class for transformations
    """
    @abstractmethod
    def transform(self, text):
        """
        a method to perform perturbation
        :param text: text to transform
        :return: list of transformed texts
        """
        pass
