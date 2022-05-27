"""Neural Network helper functions and classes."""

from abc import ABC, abstractmethod
from typing import Any


class _NeuralNet(ABC):
    """Base abstract class for all neural network models."""

    @abstractmethod
    def forward(self, x: Any) -> Any:
        """Run a forward pass of the model."""
        raise NotImplementedError


class _ConvNeuralNet(_NeuralNet, ABC):
    """Abstract class for all convolutional neural network models."""

    pass


class _FeedForwardNeuralNet(_NeuralNet, ABC):
    """Abstract class for all feed-forward neural network models."""

    pass
