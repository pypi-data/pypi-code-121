
import torch

from typing import Tuple

from .base import Permutation


class ReversePermutation(Permutation):
    """ Reverses Input """
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = x.flip(self.dim)
        logabsdet = x.new_zeros(x.shape[0])

        return z, logabsdet

    def inverse(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x = z.flip(self.dim)
        logabsdet = z.new_zeros(z.shape[0])

        return x, logabsdet
