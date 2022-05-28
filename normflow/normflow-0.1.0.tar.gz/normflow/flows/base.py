import torch
from torch.distributions import Distribution

from typing import Tuple

from normflow.common import Invertible
from normflow.transforms import Transform
from normflow import utils


class Flow(Invertible):
    """
    Base class for Normalizing Flows, consisting of a Transform and a latent Distribution
    """
    def __init__(self, transform: Transform, distribution: Distribution):
        super().__init__()
        self.transform = transform
        self.distribution = distribution

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Return the forward transform and the log likelihood for the latent samples """
        z, logabsdet = self.transform.forward(x)

        log_prob = self.distribution.log_prob(z)

        # product of probabilities is the total probability
        # in the log this turns into a sum
        log_prob = utils.mean_except_batch(log_prob)

        return z, log_prob + logabsdet

    def inverse(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Return the inverse transform """
        log_prob = self.distribution.log_prob(z)

        log_prob = utils.mean_except_batch(log_prob)

        x, logabsdet = self.transform.inverse(z)

        return x, log_prob - logabsdet
