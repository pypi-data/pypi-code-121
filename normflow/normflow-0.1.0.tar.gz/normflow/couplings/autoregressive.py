
import torch
import torch.nn as nn

from typing import Tuple

from .base import Coupling


class AutoRegressiveCoupling(Coupling):
    """ Coupling that applies an AR transform based on a set of parameters determined through a neural network """
    def __init__(self, params_network: nn.Module) -> None:
        super().__init__()
        self.params_network = params_network

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        z1 = x1
        params = self.params_network(x1)
        z2, logabsdet = self._forward(params, x2)

        return z1, z2, logabsdet

    def _forward(self, params: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError

    def inverse(self, z1: torch.Tensor, z2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        x1 = z1
        params = self.params_network(x1)
        x2, logabsdet = self._inverse(params, z2)

        return x1, x2, logabsdet

    def _inverse(self, params: torch.Tensor, z2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError
