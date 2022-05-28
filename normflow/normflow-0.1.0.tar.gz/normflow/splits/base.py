
import torch

from typing import Tuple

from normflow.common import Invertible


class Split(Invertible):
    """
    Base class for invertible input splits
    """
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        """ Create disjoint outputs from input """
        raise NotImplementedError

    def inverse(self, zs: Tuple[torch.Tensor, ...]) -> torch.Tensor:
        """ Merge disjoint inputs into output """
        raise NotImplementedError
