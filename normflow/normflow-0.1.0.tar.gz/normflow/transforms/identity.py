
import torch

from typing import Tuple

from .base import Transform


class IdentityTransform(Transform):
    """
    This transform does nothing.
    """
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = x
        logabsdet = x.new_zeros(x.shape[0])

        return z, logabsdet

    def inverse(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x = z
        logabsdet = z.new_zeros(z.shape[0])

        return x, logabsdet
