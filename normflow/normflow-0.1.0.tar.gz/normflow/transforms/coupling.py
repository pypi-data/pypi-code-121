
import torch

from typing import Tuple

from normflow.couplings import Coupling
from normflow.splits import Split
from .base import Transform


class CouplingTransform(Transform):
    """
    Wrapper class for Splits and Couplings
    A typical process order in normalizing flows is
        1. Splitting the input into two halves
        2. Transforming one half
        3. Concatenating the untransformed and transformed halves
        4. Applying some permutation
    This class takes care of 1, 2 and 3, in a generalized fashion.
    """
    def __init__(self, split: Split, coupling: Coupling) -> None:
        super().__init__()
        self.split = split
        self.coupling = coupling

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x1, x2 = self.split.forward(x)
        z1, z2, logabsdet = self.coupling.forward(x1, x2)

        return self.split.inverse((z1, z2)), logabsdet

    def inverse(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z1, z2 = self.split.forward(z)
        x1, x2, logabsdet = self.coupling.inverse(z1, z2)

        return self.split.inverse((x1, x2)), logabsdet
