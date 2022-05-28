import torch

from typing import Tuple

import normflow.utils as utils

from .autoregressive import AutoRegressiveCoupling


class AffineCoupling(AutoRegressiveCoupling):
    """
    Coupling that applies a scale and shift to inputs
    """

    def _forward(self, params: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        logscale, shift = torch.tensor_split(params, 2, -1)

        z2 = torch.exp(logscale) * x2 + shift

        logabsdet = utils.sum_except_batch(logscale)

        return z2, logabsdet

    def _inverse(self, params: torch.Tensor, z2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        logscale, shift = torch.tensor_split(params, 2, -1)

        x2 = (z2 - shift) * torch.exp(-logscale)

        logabsdet = -utils.sum_except_batch(logscale)

        return x2, logabsdet
