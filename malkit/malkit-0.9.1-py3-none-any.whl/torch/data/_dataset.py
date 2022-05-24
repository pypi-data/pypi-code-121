from pathlib import Path
from typing import Callable, Dict, List, Tuple

import pandas as pd
from torch import Tensor
from torch.utils.data import Dataset

from ..._typing import FilePath


class ClassifiedDataset(Dataset):
    def __init__(
        self,
        root: FilePath,
        labels: pd.DataFrame,
        loader: Callable[[FilePath], Tensor],
    ) -> None:
        root = Path(root)
        if not root.is_dir():
            raise ValueError(f"{root} is not a directory")

        self.root = root
        self.labels = labels
        self.loader = loader

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

    def get_sample_path(self, index: int) -> Path:
        sample_name = self.sample_names[index]
        target_name = self.target_names[index]
        sample_path = self.root / target_name / sample_name
        return sample_path

    def get_sample_path_alter(self, index: int, root: FilePath) -> Path:
        sample_name = self.sample_names[index]
        target_name = self.target_names[index]
        sample_dir = Path(root) / target_name
        sample_dir.mkdir(parents=True, exist_ok=True)
        sample_path = sample_dir / sample_name
        return sample_path

    def get_sample(self, index: int) -> Tensor:
        sample_path = self.get_sample_path(index)
        sample = self.loader(sample_path)
        return sample

    def get_target(self, index: int) -> int:
        target_name = self.target_names[index]
        target = self.class_to_index[target_name]
        return target

    def __getitem__(self, index: int) -> Tuple[Tensor, int]:
        sample_name = self.sample_names[index]
        target_name = self.target_names[index]
        sample_path = self.root / target_name / sample_name
        sample = self.loader(sample_path)
        target = self.class_to_index[target_name]
        return sample, target

    def __len__(self) -> int:
        return len(self.sample_names)

    def __repr__(self) -> str:
        s = f"{type(self).__name__}:\n"
        s += f"    Root: {self.root}\n"
        s += f"    Loader: {self.loader}\n"
        s += f"    Number of samples: {len(self)}\n"
        s += f"    Number of classes: {len(self.index_to_class)}\n"
        return s
