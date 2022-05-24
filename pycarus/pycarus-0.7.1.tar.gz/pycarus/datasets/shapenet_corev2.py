from pathlib import Path
from typing import Callable, List, Tuple

import h5py  # type: ignore
import torch
from torch import Tensor
from torch.utils.data import Dataset

from pycarus.transforms.var import Compose


class ShapeNetCoreV2(Dataset):
    def __init__(
        self,
        root: Path,
        split: str,
        download: bool = False,
        transforms: List[Callable] = [],
    ) -> None:
        """Create ShapeNetCoreV2 dataset.

        Args:
            root: The directory that contains the dataset.
            split: The required split, it can be "train", "val", "test" or a combination of them,
                   i.e. "trainval", "traintest" or "trainvaltest".
            download: If True download the dataset using the "tmp" folder. Defaults to False.
            transforms: The list of transforms to apply to pcds. Defaults to [].
        """
        super().__init__()

        assert split in ["train", "test", "val", "trainval", "traintest", "trainvaltest"]
        self.split = split

        self.dataset_root = root

        if download:
            if self.dataset_root.exists():
                print("Dataset root already exists, not downloading.")
            else:
                self.download()

        h5_files: List[Path] = []
        for s in ["train", "val", "test"]:
            if s in self.split:
                h5_files.extend(list(self.dataset_root.glob(f"*{s}*.h5")))
        h5_files.sort()

        self.pcds, self.labels = self.load_h5(h5_files)

        self.transform = Compose(transforms)

        with open(self.dataset_root / "shape_names.txt") as f:
            self.shape_names = [line.strip() for line in f.readlines()]

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

    def download(self) -> None:
        """Function to download the dataset."""
        raise NotImplementedError("Function not implemented.")
