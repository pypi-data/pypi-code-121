
import torch.nn as nn


class Invertible(nn.Module):
    """
    Base class for invertible modules
    Each Invertible must define both the forward and inverse method
    """
    def forward(self, *args, **kwargs):
        raise NotImplementedError

    def inverse(self, *args, **kwargs):
        raise NotImplementedError
