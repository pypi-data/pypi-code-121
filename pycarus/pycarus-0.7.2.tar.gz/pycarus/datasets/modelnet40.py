from pathlib import Path
from typing import Callable, List, Tuple

import h5py  # type: ignore
import torch
from torch import Tensor
from torch.utils.data import Dataset

from pycarus.transforms.var import Compose


class ModelNet40(Dataset):
    def __init__(
        self,
        root: Path,
        split: str,
        transforms: List[Callable] = [],
    ) -> None:
        """Create ModelNet40 dataset.

        Splits are obtained according to the paper:
        "Revisiting Point Cloud Shape Classification with a Simple and Effective Baseline",
        Ankit Goyal, Hei Law, Bowei Liu, Alejandro Newell, Jia Deng.

        Args:
            root: The directory that contains the dataset.
            split: The required split. Available splits are:
                - "train",  the training set without the validation split.
                - "test", the standard test set.
                - "val", the validation split.
                - "train_and_val", the training set with the validation split.
            transforms: The list of transforms to apply to pcds. Defaults to [].
        """
        super().__init__()

        assert split in ["train_and_val", "val", "train", "test"]
        self.split = split

        self.dataset_root = root

        h5_files = [self.dataset_root / f for f in self.get_h5_files_from_split(self.split)]
        h5_files.sort()

        self.pcds, self.labels = self.load_h5(h5_files)

        self.transform = Compose(transforms)

        with open(self.dataset_root / "shape_names.txt") as f:
            self.shape_names = [line.strip() for line in f.readlines()]

    def get_h5_files_from_split(self, split: str) -> List[str]:
        """Get the h5 files to be loaded according to the given split.

        Args:
            split: The required split.

        Returns:
            The list of h5 files to be loaded.
        """
        files = {
            "train_and_val": ["train_no_val.h5", "val.h5"],
            "train": ["train_no_val.h5"],
            "val": ["val.h5"],
            "test": ["test_0.h5", "test_1.h5"],
        }
        return files[split]

    @staticmethod
    def load_h5(paths: List[Path]) -> Tuple[Tensor, Tensor]:
        """Load all the given h5 files.

        Args:
            paths: The list of paths to the h5 files to load.

        Returns:
            - One tensor with all the pcds, with shape (NUM_PCDS, NUM_POINTS, 3).
            - One tensor with all the labels, with shape (NUM_PCDS,).
        """
        all_pcds: List[Tensor] = []
        all_labels: List[Tensor] = []
        for h5_path in paths:
            f = h5py.File(h5_path, "r+")
            pcds = f["data"][:].astype("float32")
            labels = f["label"][:].astype("int64")
            f.close()
            all_pcds.append(torch.from_numpy(pcds))
            all_labels.append(torch.from_numpy(labels))
        return torch.cat(all_pcds, dim=0), torch.cat(all_labels, dim=0).squeeze(1)

    def __len__(self) -> int:
        """Return the number of pcds in the dataset.

        Returns:
            The number of pcds in the dataset.
        """
        return self.pcds.shape[0]

    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        """Return the pcd and the label at the given index.

        Args:
            index: The index of the required element.

        Returns:
            - A tensor with the point cloud with shape (NUM_POINTS, 3).
            - A tensor with the label.
        """
        pcd, label = self.pcds[index], self.labels[index]

        pcd = self.transform(pcd)

        return pcd, label

    def get_class_name(self, label: int) -> str:
        return self.shape_names[label]
