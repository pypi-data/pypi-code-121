
import torch
import torch.nn as nn

from typing import Tuple

from unstable import unstable

from .base import Transform


@unstable
class ActNorm(Transform):
    """
    Activation Norm as described by:
    Kingma et al.
    Glow: Generative Flow with Invertible 1x1 Convolutions
    """
    def __init__(self):
        super().__init__()
        self.scale = None
        self.shift = None

        # should register this as a buffer, so it gets saved alongside the model
        self.register_buffer("initialized", torch.tensor(False))

    def initialize_(self, x: torch.Tensor) -> None:
        std, mean = torch.std_mean(x.detach().reshape(x.shape[0], -1), dim=0, unbiased=False)
        self.scale = nn.Parameter(1 / std)
        self.shift = nn.Parameter(-mean)
        self.initialized = torch.tensor(True)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        if not self.initialized:
            self.initialize_(x)

        z = self.scale * x + self.shift

        logabsdet = torch.log(torch.abs(self.scale))

        return z, logabsdet

    def inverse(self, z: torch.Tensor) -> torch.Tensor:
        x = (z - self.shift) / self.scale

        return x
