
import torch

from typing import Tuple

from ..base import Transform


class Permutation(Transform):
    """ Permute Input on a Given Dimension """

    def __init__(self, dim: int = -1) -> None:
        super().__init__()
        self.dim = dim

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Perform the Forward Permutation """
        raise NotImplementedError

    def inverse(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Perform the Inverse Permutation """
        raise NotImplementedError
