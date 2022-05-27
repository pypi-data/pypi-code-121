"""Pytorch implementation of the tensor shim."""
from __future__ import annotations

from typing import Any, ClassVar, List, Sequence, Union, cast

import numpy as np
import torch

from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.federated.shim import BackendTensorShim
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _TensorLike,
)


class PyTorchBackendTensorShim(BackendTensorShim, _BaseSerializableObjectMixIn):
    """PyTorch backend shim/bridge for converting from/to PyTorch tensors."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    @staticmethod
    def to_numpy(t: Union[_TensorLike, List[float]]) -> np.ndarray:
        """See base class."""
        if isinstance(t, _AdaptorForPyTorchTensor):
            array_t = t.torchtensor.numpy()
        else:
            array_t = np.asarray(t)
        return cast(np.ndarray, array_t)

    @staticmethod
    def to_tensor(p: Sequence, **kwargs: Any) -> _TensorLike:
        """See base class."""
        return _AdaptorForPyTorchTensor(torch.tensor(p, **kwargs))

    @staticmethod
    def to_list(p: Union[np.ndarray, _TensorLike]) -> List[float]:
        """See base class."""
        if isinstance(p, np.ndarray):
            return cast(List[float], p.tolist())
        elif isinstance(p, _AdaptorForPyTorchTensor):
            return p.torchtensor.tolist()
        else:
            raise TypeError("Unexpected type")

    @staticmethod
    def is_tensor(p: Any) -> bool:
        """See base class."""
        is_tensor: bool = torch.is_tensor(p)
        return is_tensor
