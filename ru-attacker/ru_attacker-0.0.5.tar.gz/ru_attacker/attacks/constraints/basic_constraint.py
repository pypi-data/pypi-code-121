from abc import ABC, abstractmethod

__all__ = ["BasicConstraint"]


class BasicConstraint(ABC):
    """
    A basic class for constraints
    """
    @abstractmethod
    def check(self, original, transformed):
        """
        a method that checks whether the perturbation satisfies the constraint
        :param original: original sample
        :param transformed: transformed sample
        :return: True/False
        """
        pass
