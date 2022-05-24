from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset

from .._typing import FilePath

__all__ = [
    "LabeledDataset",
    "LabeledByteSeqDataset",
    "LabeledImageDataset",
    "UnlabeledDataset",
    "UnlabeledByteSeqDataset",
    "UnlabeledImageDataset",
]


class ByteSeqLoader:
    def __init__(self, length: int, padding: int = 256) -> None:
        self.length = length
        self.padding = padding

    def __call__(self, path: FilePath) -> torch.Tensor:
        with open(path, "rb") as f:
            buffer = f.read(self.length)

        # Since PyTorch embedding layer requires int32/int64 as input, we have
        # to convert uint8 to int32.
        byte_seq: np.ndarray = np.frombuffer(buffer, dtype=np.uint8)
        byte_seq = byte_seq.astype(np.int32)

        padding_length = self.length - len(byte_seq)
        if padding_length > 0:
            padding_seq = np.full(padding_length, self.padding, dtype=np.int32)
            byte_seq = np.concatenate([byte_seq, padding_seq])
        return torch.tensor(byte_seq)


class PILLoader:
    def __init__(self, mode: Optional[str] = None) -> None:
        self.mode = mode

    def __call__(self, path: FilePath) -> Image.Image:
        with open(path, "rb") as f:
            image = Image.open(f)
            return image.convert(self.mode)


class LabeledDataset(Dataset):
    def __init__(
        self,
        root: FilePath,
        loader: Callable[[FilePath], Any],
        labels: pd.DataFrame,
        *,
        cat: bool = True,
        suffix: Optional[str] = None,
    ) -> None:
        self.root = Path(root)
        self.loader = loader
        self.labels = labels
        self.cat = cat
        self.suffix = suffix

        self._sample_names = [str(item) for item in labels.iloc[:, 0]]
        self._target_names = [str(item) for item in labels.iloc[:, 1]]

        self._index_to_class = sorted(set(self._target_names))
        self._class_to_index = {c: i for i, c in enumerate(self._index_to_class)}

    @property
    def sample_names(self) -> List[str]:
        return self._sample_names

    @property
    def target_names(self) -> List[str]:
        return self._target_names

    @property
    def index_to_class(self) -> List[str]:
        return self._index_to_class

    @property
    def class_to_index(self) -> Dict[str, int]:
        return self._class_to_index

    def __getitem__(self, index: int) -> Tuple[Any, int]:
        sample_name = self._sample_names[index]
        target_name = self._target_names[index]

        if self.cat:
            sample_path = self.root / target_name / sample_name
        else:
            sample_path = self.root / sample_name

        # If ``suffix`` is an empty string, the suffix will be removed.
        if self.suffix is not None:
            sample_path = sample_path.with_suffix(self.suffix)

        sample = self.loader(sample_path)
        target = self._class_to_index[target_name]
        return sample, target

    def __len__(self) -> int:
        return len(self.labels)

    def __repr__(self) -> str:
        args = ", ".join(f"{a}={getattr(self, a)!r}" for a in self._args())
        s = f"{type(self).__name__}({args}):\n"
        s += f"    Root directory: {self.root}\n"
        s += f"    Number of samples: {len(self)}\n"
        s += f"    Number of classes: {len(self.index_to_class)}\n"
        return s

    def _args(self) -> Tuple[str, ...]:
        return ("cat", "suffix")


class LabeledByteSeqDataset(LabeledDataset):
    def __init__(
        self,
        root: FilePath,
        labels: pd.DataFrame,
        *,
        cat: bool = True,
        suffix: Optional[str] = ".binary",
        length: int,
        padding: int = 256,
    ) -> None:
        loader = ByteSeqLoader(length, padding)
        super().__init__(root, loader, labels, cat=cat, suffix=suffix)
        self.length = length
        self.padding = padding

    def _args(self) -> Tuple[str, ...]:
        return super()._args() + ("length", "padding")


class LabeledImageDataset(LabeledDataset):
    def __init__(
        self,
        root: FilePath,
        labels: pd.DataFrame,
        *,
        cat: bool = True,
        suffix: Optional[str] = ".png",
        loader_mode: Optional[str] = "L",
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ) -> None:
        loader = PILLoader(loader_mode)
        super().__init__(root, loader, labels, cat=cat, suffix=suffix)
        self.loader_mode = loader_mode
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, index: int) -> Tuple[Any, int]:
        sample, target = super().__getitem__(index)
        if self.transform is not None:
            sample = self.transform(sample)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return sample, target

    def _args(self) -> Tuple[str, ...]:
        return super()._args() + ("loader_mode",)


class UnlabeledDataset(Dataset):
    def __init__(
        self,
        root: FilePath,
        loader: Callable[[FilePath], Any],
        *,
        suffix: Optional[str] = None,
    ) -> None:
        self.root = Path(root)
        self.loader = loader
        self.suffix = suffix

        self._sample_paths = sorted(entry for entry in self.root.iterdir())

    def __getitem__(self, index: int) -> Tuple[Any, str]:
        sample_path = self._sample_paths[index]

        if self.suffix is not None:
            sample_name = sample_path.with_suffix(self.suffix).name
        else:
            sample_name = sample_path.name

        sample = self.loader(sample_path)
        return sample, sample_name

    def __len__(self) -> int:
        return len(self._sample_paths)

    def __repr__(self) -> str:
        args = ", ".join(f"{a}={getattr(self, a)!r}" for a in self._args())
        s = f"{type(self).__name__}({args}):\n"
        s += f"    Root directory: {self.root}\n"
        s += f"    Number of samples: {len(self)}\n"
        return s

    def _args(self) -> Tuple[str, ...]:
        return ("suffix",)


class UnlabeledByteSeqDataset(UnlabeledDataset):
    def __init__(
        self,
        root: FilePath,
        *,
        suffix: Optional[str] = "",
        length: int,
        padding: int = 256,
    ) -> None:
        loader = ByteSeqLoader(length, padding)
        super().__init__(root, loader, suffix=suffix)
        self.length = length
        self.padding = padding

    def _args(self) -> Tuple[str, ...]:
        return super()._args() + ("length", "padding")


class UnlabeledImageDataset(UnlabeledDataset):
    def __init__(
        self,
        root: FilePath,
        *,
        suffix: Optional[str] = "",
        loader_mode: Optional[str] = "L",
        transform: Optional[Callable] = None,
    ) -> None:
        loader = PILLoader(loader_mode)
        super().__init__(root, loader, suffix=suffix)
        self.loader_mode = loader_mode
        self.transform = transform

    def __getitem__(self, index: int) -> Tuple[Any, str]:
        sample, sample_name = super().__getitem__(index)
        if self.transform is not None:
            sample = self.transform(sample)
        return sample, sample_name

    def _args(self) -> Tuple[str, ...]:
        return super()._args() + ("loader_mode",)
