
import torch

from typing import Tuple

from normflow.common import Invertible


class Coupling(Invertible):
    """ Base Class for Couplings, Which Transform a Part of Their Input Depending on Another Part of the Input """
    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward transform x2 based on x1
        @param x1: First Input Part
        @param x2: Second Input Part
        @return: z1, z2, log abs det J
        """
        raise NotImplementedError

    def inverse(self, z1: torch.Tensor, z2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """ Inverse Transform z2 based on z1 """
        raise NotImplementedError
