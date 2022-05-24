from typing import Tuple

import numpy as np
import torch
from torch import Tensor

from ..._typing import FilePath
from ._loader import Loader

__all__ = ["BinaryLoader"]


class BinaryLoader(Loader):
    def __init__(self, length: int, padding_value: int = 256) -> None:
        self.length = length
        self.padding_value = padding_value

    def __call__(self, path: FilePath) -> Tensor:
        with open(path, "rb") as f:
            buffer = f.read(self.length)
        return self._from_buffer(buffer)

    def from_buffer(self, buffer: bytes) -> Tensor:
        return self._from_buffer(buffer[: self.length])

    def _from_buffer(self, buffer: bytes) -> Tensor:
        # Since PyTorch embedding layer requires int32/int64 as input, we have
        # to convert uint8 to int32.
        binary = np.frombuffer(buffer, dtype=np.uint8)
        binary = binary.astype(np.int32)

        padding_length = self.length - len(binary)
        if padding_length > 0:
            padding = np.full(padding_length, self.padding_value, dtype=np.int32)
            binary = np.concatenate([binary, padding])
        return torch.tensor(binary)

    def _get_args(self) -> Tuple[str, ...]:
        return ("length", "padding_value")
