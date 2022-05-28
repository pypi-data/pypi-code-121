import torch
import torch.nn as nn

from typing import Tuple

from .base import Coupling


class AdditiveCoupling(Coupling):
    """
    A special case of the affine coupling where s = 1 and log det J = 0
    """
    def __init__(self, shift: nn.Module):
        super().__init__()
        self.shift = shift

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        z1 = x1
        z2 = x2 + self.shift(x1)

        logabsdet = x1.new_zeros(x1.shape[0])

        return z1, z2, logabsdet

    def inverse(self, z1: torch.Tensor, z2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        x1 = z1
        x2 = z2 - self.shift(x1)

        logabsdet = z1.new_zeros(z1.shape[0])

        return x1, x2, logabsdet
