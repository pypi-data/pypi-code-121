"""Predictor base class."""
from abc import ABC, abstractmethod

class Predictor(ABC):
    """Base class for all predictors."""
    @classmethod
    @abstractmethod
    def load(cls, filename):
        """
        Loads a model.

        Args:
            filename: string.

        Returns:
            Model.
        """
        pass

    @abstractmethod
    def save(self, filename):
        """
        Saves model to file.

        Args:
            filename: string.

        Returns:
            None.
        """
        pass