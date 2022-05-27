"""Type Variable for our PyTorch Models."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Tuple, Type, Union

import torch

from bitfount.types import _TensorLike


class _AdaptorForPyTorchTensor(_TensorLike):
    """Adapter protocol for pytorch Tensor.

    This is a thin wrapper around a pytorch tensor. It is required to provide definitive
    type annotations for different tensor operations.
    """

    def __init__(self, tensor: torch.Tensor):
        self.torchtensor = tensor

    def __mul__(self, other: Any) -> _AdaptorForPyTorchTensor:
        return _AdaptorForPyTorchTensor(self.torchtensor * other)

    def __sub__(self, other: Any) -> _AdaptorForPyTorchTensor:
        return _AdaptorForPyTorchTensor(self.torchtensor - other)

    def squeeze(self, axis: Optional[Any] = None) -> _AdaptorForPyTorchTensor:
        """Returns a tensor with all the dimensions of input of size 1 removed."""
        if axis:
            return _AdaptorForPyTorchTensor(torch.squeeze(self.torchtensor, dim=axis))
        else:
            return _AdaptorForPyTorchTensor(torch.squeeze(self.torchtensor))


# Pytorch Types

# Pytorch Weight Dict

PytorchWeightDict = Dict[str, Type[_AdaptorForPyTorchTensor]]
PytorchWeightMapping = Mapping[str, Type[_AdaptorForPyTorchTensor]]

# Pytorch Batch types:
ImgAndTabBatch = Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
TabxorImgBatch = Tuple[torch.Tensor, torch.Tensor]

# SplitDataloaderTypes:
ImgAndTabDataSplit = Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
ImgXorTabDataSplit = Tuple[torch.Tensor, torch.Tensor]

TabDataReturnType = Tuple[
    Tuple[torch.Tensor, torch.Tensor], torch.Tensor, Optional[torch.Tensor]
]
ImgDataReturnType = Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]

# Pytorch forward input types
ImgFwdTypes = Union[List[torch.Tensor], torch.Tensor]
TabFwdTypes = Tuple[torch.Tensor, torch.Tensor]
