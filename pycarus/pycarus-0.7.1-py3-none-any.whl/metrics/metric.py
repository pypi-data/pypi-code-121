from abc import ABC, abstractmethod
from typing import Any

import torch
from torch import nn


class Metric(nn.Module, ABC):
    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> None:
        self.update(predictions, targets)

    @abstractmethod
    def reset(self) -> None:
        """Reset metric status."""

    @abstractmethod
    def update(self, predictions: torch.Tensor, targets: torch.Tensor) -> None:
        """Update metric status.

        Args:
            predictions: A batch of predictions.
            targets: A batch of targets.
        """

    @abstractmethod
    def compute(self) -> Any:
        """Compute overall result."""
