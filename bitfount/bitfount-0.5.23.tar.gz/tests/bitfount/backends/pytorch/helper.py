"""Contains helper methods for PyTorch model tests."""
from typing import Mapping

import torch

from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.types import _TensorLike


def get_params_mean(model_state_dict: Mapping[str, _TensorLike]) -> torch.Tensor:
    """Gets the parameter means from the model state dict.

    Returns the mean of all relevant neural network model parameters.
    """
    params_lst = []
    for k, v in dict(model_state_dict).items():
        if any(i in k for i in ("embeddings", "layers", "heads", "bias")):
            if isinstance(v, _AdaptorForPyTorchTensor):
                params_lst.append(v.torchtensor.sum())
    return torch.tensor(params_lst).mean()
