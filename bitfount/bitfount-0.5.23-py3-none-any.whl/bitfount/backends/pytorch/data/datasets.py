"""PyTorch implementations for Bitfount Dataset classes."""
from typing import Sequence, Union

import torch
from torch.utils.data import Dataset as PTDataset
from torch.utils.data import IterableDataset as PTIterableDataset

from bitfount.backends.pytorch.data.utils import _index_tensor_handler
from bitfount.data.datasets import _BitfountDataset, _IterableBitfountDataset
from bitfount.data.types import _DataEntry


class _PyTorchDataset(_BitfountDataset, PTDataset):
    """See base class."""

    def __getitem__(self, idx: Union[int, Sequence[int], torch.Tensor]) -> _DataEntry:
        idx = _index_tensor_handler(idx)
        return self._getitem(idx)


class _PyTorchIterableDataset(_IterableBitfountDataset, PTIterableDataset):
    """See base class."""

    pass
