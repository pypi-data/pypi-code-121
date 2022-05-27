from pathlib import Path
from typing import Callable, List, Tuple, Union

import torch
from torch import Tensor
from torch.utils.data import Dataset

from pycarus.geometry.pcd import read_pcd
from pycarus.transforms.var import Compose


class PlyDataset(Dataset):
    def __init__(
        self,
        root: Union[str, Path],
        split: str,
        transforms: List[Callable] = [],
    ) -> None:
        """Generic dataset to load point clouds stored as PLY files.

        Point clouds are expected to be stored in separate subfolders inside "root",
        one subfolder for each class. Each subfolder is expected to contain
        separate subfolders for each split.
        Class IDs are computed by sorting the class names in alphabetical order.

        Args:
            root: The path to the directory with the dataset.
            transforms: The list of transforms to be applied to the point clouds.
        """
        super().__init__()

        self.root = Path(root)

        self.classes = sorted([s.name for s in self.root.iterdir()])

        self.pcds: List[Tensor] = []
        self.labels: List[Tensor] = []

        for i, c in enumerate(self.classes):
            class_path = self.root / c / split

            items_paths = sorted(list(class_path.glob("*.ply")))
            for p in items_paths:
                self.pcds.append(read_pcd(p))
                self.labels.append(torch.tensor(i, dtype=torch.long))

        self.transform = Compose(transforms)

    def __len__(self) -> int:
        """Return the number of pcds in the dataset.

        Returns:
            The number of pcds in the dataset.
        """
        return len(self.pcds)

    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        """Return the pcd and the label at the given index.

        Args:
            index: The index of the required element.

        Returns:
            - A tensor with the point cloud with shape (NUM_POINTS, 3).
            - A tensor with the label.
        """
        pcd = self.transform(self.pcds[index])
        return pcd, self.labels[index]

    def get_class(self, label: int) -> str:
        """Return the name of the class with the given label.

        Args:
            label: The numeric label of the required class.

        Returns:
            The name of the class corresponding to the given label.
        """
        return self.classes[label]
