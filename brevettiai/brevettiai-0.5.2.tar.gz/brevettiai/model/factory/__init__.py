"""
Factory for configuration of implemented tensorflow models
"""

from tensorflow.python.keras.engine.functional import Functional
from abc import ABC, abstractmethod
from pydantic import BaseModel


class ModelFactory(ABC, BaseModel):
    """Abstract model factory class"""

    @staticmethod
    def custom_objects():
        """Custom objects used by the model"""
        return {}

    @abstractmethod
    def build(self, input_shape, output_shape, **kwargs) -> Functional:
        """Function to build segmentation backbone"""
