
import torch

from typing import Tuple

from .base import Split


class MaskedSplit(Split):
    """
    Split input by using a fixed mask.
    """
    def __init__(self, mask: torch.Tensor):
        super().__init__()
        self.mask = mask

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        # TODO: keep dims?
        m = self.mask.to(x.device)
        z1, z2 = x[m], x[~m]
        return z1, z2

    def inverse(self, zs: Tuple[torch.Tensor, ...]) -> torch.Tensor:
        # TODO: infer batch dimension, which is typically missing from the mask
        z1, z2 = zs
        x = torch.zeros_like(self.mask, dtype=z1.dtype).to(z1.device)
        m = self.mask.to(z1.device)
        x[m] = z1
        x[~m] = z2

        return x
