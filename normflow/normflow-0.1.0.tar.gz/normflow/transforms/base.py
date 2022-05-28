
import torch

from typing import Tuple

from normflow.common import Invertible


class Transform(Invertible):
    """
    Base class for invertible transforms as needed by normalizing flows
    """
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Return the forward transform and log(|det J|) where J is the corresponding Jacobian """
        raise NotImplementedError

    def inverse(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Return the inverse transform and log(|det J|) """
        raise NotImplementedError
