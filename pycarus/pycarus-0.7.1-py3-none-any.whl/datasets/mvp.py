from pathlib import Path
from typing import Callable, List, Tuple

import h5py  # type: ignore
import numpy as np
import torch
import torch.utils.data as data
from torch import Tensor

from pycarus.transforms.var import Compose

T_ITEM = Tuple[str, str, Tensor, Tensor]


class Mvp(data.Dataset):
    CATEGORIES = [
        "02691156",
        "02933112",
        "02958343",
        "03001627",
        "03636649",
        "04256520",
        "04379243",
        "04530566",
        "02818832",
        "02828884",
        "02871439",
        "02924116",
        "03467517",
        "03790512",
        "03948459",
        "04225987",
    ]

    def __init__(
        self,
        root: Path,
        split: str,
        num_points: int = 2048,
        categories: List[str] = [],
        transforms_complete: List[Callable] = [],
        transforms_incomplete: List[Callable] = [],
        transforms_all: List[Callable] = [],
    ) -> None:
        """Class implementing the MVP dataset as proposed in:

        Pan, L., Chen, X., Cai, Z., Zhang, J., Zhao, H., Yi, S., & Liu, Z. (2021).
        Variational Relational Point Completion Network.
        In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 8524-8533).

        Args:
            root: The path to the folder containing the dataset.
            split: The name of the split to load. Allowed values: train, val, train_and_val, test.
            num_points: The resolution for groundtruth clouds. Allowed values: 2048, 4096, 8192, 16384.
            categories: A list of categories ids to select. Defaults to [] (keep all categories).
            transforms_complete: The transforms to apply to the complete clouds. Defaults to [].
            transforms_incomplete: The transforms to apply to the incomplete clouds. Defaults to [].
            transforms_all: The transforms to apply to both the complete
                and the incomplete clouds. Defaults to [].
        """
        splits = ["train", "val", "train_and_val", "test"]
        if split not in splits:
            raise ValueError(f"Split {split} not allowed, only {splits} are allowed.")

        self.num_points = num_points
        res_gt = [2048, 4096, 8192, 16384]
        if self.num_points not in res_gt:
            raise ValueError(f"{self.num_points} value not allowed, only {res_gt} are allowed.")

        self.transform_complete = Compose(transforms_complete)
        self.transform_incomplete = Compose(transforms_incomplete)
        self.transform_all = Compose(transforms_all)

        split_file = split if split not in ["val", "train_and_val"] else "train"
        self.path_inc = root / f"mvp_{split_file}_input.h5"
        file_inc = h5py.File(self.path_inc, "r")
        self.incompletes = np.array(file_inc.get("incomplete_pcds"))
        self.labels = np.array(file_inc.get("labels"))
        incompletes_novel = np.array(file_inc.get("novel_incomplete_pcds"))
        labels_novel = np.array(file_inc.get("novel_labels"))
        file_inc.close()

        self.path_comp = root / f"mvp_{split_file}_gt_{self.num_points}pts.h5"
        file_comp = h5py.File(self.path_comp, "r")
        self.completes = np.array(file_comp.get("complete_pcds"))
        completes_novel = np.array(file_comp.get("novel_complete_pcds"))
        file_comp.close()

        self.incompletes = np.concatenate((self.incompletes, incompletes_novel), axis=0)
        self.completes = np.concatenate((self.completes, completes_novel), axis=0)
        self.labels = np.concatenate((self.labels, labels_novel), axis=0)

        indices = list(range(self.incompletes.shape[0]))

        if split != "test":
            with open(root / "val_shapes.txt") as f:
                val_shapes = [int(line.strip()) for line in f.readlines()]

            val_indices: List[int] = []
            for idx in val_shapes:
                start = idx * 26
                end = start + 26
                val_indices.extend(range(start, end))

            train_indices = [idx for idx in indices if idx not in val_indices]

            if split == "train":
                indices = train_indices
            elif split == "val":
                indices = val_indices
            else:
                indices = sorted(train_indices + val_indices)

        if len(categories) == 0:
            self.indices = list(range(self.incompletes.shape[0]))
        else:
            self.indices = []

            for index in range(self.incompletes.shape[0]):
                label = int(self.labels[index])
                if Mvp.CATEGORIES[label] in categories:
                    self.indices.append(index)

    def __len__(self) -> int:
        """Return the number of items in the dataset.

        Returns:
            The number of items in the dataset.
        """
        return len(self.indices)

    def __getitem__(self, index: int) -> T_ITEM:
        """Return one item of the dataset.

        Args:
            index: The index of the required item.

        Returns:
            - The category of the item.
            - The name of the item formatted as "s{shape_index}_v{view_index}".
            - A tensor with the incomplete point cloud with shape (NUM_POINTS, 3).
            - A tensor with the complete point cloud with shape (NUM_POINTS, 3).
        """
        idx = self.indices[index]
        idx_complete = idx // 26
        idx_view = idx % 26

        incomplete = torch.from_numpy((self.incompletes[idx]))
        complete = torch.from_numpy((self.completes[idx_complete]))

        incomplete = self.transform_all(self.transform_incomplete(incomplete))
        complete = self.transform_all(self.transform_complete(complete))

        label = torch.tensor(self.labels[idx], dtype=torch.long)
        category = Mvp.CATEGORIES[label]
        name = f"s{idx_complete}_v{idx_view:02d}"

        return category, name, incomplete, complete
