from pathlib import Path
from typing import Callable, List, Tuple

import h5py  # type: ignore
import open3d as o3d  # type: ignore
import torch
from torch import Tensor
from torch.utils.data import Dataset

from pycarus.geometry.pcd import get_o3d_pcd_from_tensor
from pycarus.transforms.var import Compose

T_ITEM = Tuple[Tensor, Tensor, Tensor]


class ShapeNetPartSegmentation(Dataset):
    """Class representing the ShapeNet part segmentation dataset as presented in:

    Yi, Li, et al. "A scalable active framework for region annotation in 3d shape collections."
    ACM Transactions on Graphics (ToG) 35.6 (2016): 1-12.
    """

    class_to_parts = {
        "02691156": [0, 1, 2, 3],
        "02773838": [4, 5],
        "02954340": [6, 7],
        "02958343": [8, 9, 10, 11],
        "03001627": [12, 13, 14, 15],
        "03261776": [16, 17, 18],
        "03467517": [19, 20, 21],
        "03624134": [22, 23],
        "03636649": [24, 25, 26, 27],
        "03642806": [28, 29],
        "03790512": [30, 31, 32, 33, 34, 35],
        "03797390": [36, 37],
        "03948459": [38, 39, 40],
        "04099429": [41, 42, 43],
        "04225987": [44, 45, 46],
        "04379243": [47, 48, 49],
    }

    part_colors = torch.tensor(
        [
            [0.65, 0.95, 0.05],
            [0.35, 0.05, 0.35],
            [0.65, 0.35, 0.65],
            [0.95, 0.95, 0.65],
            [0.95, 0.65, 0.05],
            [0.35, 0.05, 0.05],
            [0.65, 0.05, 0.05],
            [0.65, 0.35, 0.95],
            [0.05, 0.05, 0.65],
            [0.65, 0.05, 0.35],
            [0.05, 0.35, 0.35],
            [0.65, 0.65, 0.35],
            [0.35, 0.95, 0.05],
            [0.05, 0.35, 0.65],
            [0.95, 0.95, 0.35],
            [0.65, 0.65, 0.65],
            [0.95, 0.95, 0.05],
            [0.65, 0.35, 0.05],
            [0.35, 0.65, 0.05],
            [0.95, 0.65, 0.95],
            [0.95, 0.35, 0.65],
            [0.05, 0.65, 0.95],
            [0.65, 0.95, 0.65],
            [0.95, 0.35, 0.95],
            [0.05, 0.05, 0.95],
            [0.65, 0.05, 0.95],
            [0.65, 0.05, 0.65],
            [0.35, 0.35, 0.95],
            [0.95, 0.95, 0.95],
            [0.05, 0.05, 0.05],
            [0.05, 0.35, 0.95],
            [0.65, 0.95, 0.95],
            [0.95, 0.05, 0.05],
            [0.35, 0.95, 0.35],
            [0.05, 0.35, 0.05],
            [0.05, 0.65, 0.35],
            [0.05, 0.95, 0.05],
            [0.95, 0.65, 0.65],
            [0.35, 0.95, 0.95],
            [0.05, 0.95, 0.35],
            [0.95, 0.35, 0.05],
            [0.65, 0.35, 0.35],
            [0.35, 0.95, 0.65],
            [0.35, 0.35, 0.65],
            [0.65, 0.95, 0.35],
            [0.05, 0.95, 0.65],
            [0.65, 0.65, 0.95],
            [0.35, 0.05, 0.95],
            [0.35, 0.65, 0.95],
            [0.35, 0.05, 0.65],
        ]
    )

    def __init__(self, root: Path, split: str, transforms: List[Callable] = []) -> None:
        """Create an instance of ShapeNetPartSegmentation dataset.

        Args:
            root: The path to the root directory of the dataset.
            split: The split to use (only "train", "val" and "test" allowed).
            transforms: The transform to apply to the point clouds. Defaults to [].
        """
        super().__init__()

        assert split in ["train", "val", "test"]

        h5_files = [root / f for f in self.get_h5_files_from_split(split)]
        h5_files.sort()

        self.pcds, self.labels, self.part_labels = self.load_h5(h5_files)

        self.transform = Compose(transforms)

        with open(root / "all_object_categories.txt") as f:
            self.class_names = [line.strip().split("\t")[0] for line in f.readlines()]

    def get_h5_files_from_split(self, split: str) -> List[str]:
        """Get the h5 files to be loaded according to the given split.

        Args:
            split: The required split.

        Returns:
            The list of h5 files to be loaded.
        """
        files = {
            "train": [
                "ply_data_train0.h5",
                "ply_data_train1.h5",
                "ply_data_train2.h5",
                "ply_data_train3.h5",
                "ply_data_train4.h5",
                "ply_data_train5.h5",
            ],
            "val": ["ply_data_val0.h5"],
            "test": ["ply_data_test0.h5", "ply_data_test1.h5"],
        }
        return files[split]

    @staticmethod
    def load_h5(paths: List[Path]) -> Tuple[Tensor, Tensor, Tensor]:
        """Load all the given h5 files.

        Args:
            paths: The list of paths to the h5 files to load.

        Returns:
            - One tensor with all the pcds, with shape (NUM_PCDS, NUM_POINTS, 3).
            - One tensor with all the class labels, with shape (NUM_PCDS,).
            - One tensor with all the part labels, with shape (NUM_PCDS, NUM_POINTS,).
        """
        all_pcds: List[Tensor] = []
        all_labels: List[Tensor] = []
        all_part_labels: List[Tensor] = []

        for h5_path in paths:
            f = h5py.File(h5_path, "r+")
            pcds = f["data"][:].astype("float32")
            labels = f["label"][:].astype("int64")
            part_labels = f["pid"][:].astype("int64")
            f.close()
            all_pcds.append(torch.from_numpy(pcds))
            all_labels.append(torch.from_numpy(labels))
            all_part_labels.append(torch.from_numpy(part_labels))

        all_pcds_t = torch.cat(all_pcds, dim=0)
        all_labels_t = torch.cat(all_labels, dim=0).squeeze(-1)
        all_part_labels_t = torch.cat(all_part_labels, dim=0).squeeze(-1)

        return all_pcds_t, all_labels_t, all_part_labels_t

    def __len__(self) -> int:
        """Return the number of pcds in the dataset.

        Returns:
            The number of pcds in the dataset.
        """
        return self.pcds.shape[0]

    def __getitem__(self, index: int) -> T_ITEM:
        """Return the pcd, the class label and the part labels at the given index.

        Args:
            index: The index of the required element.

        Returns:
            - A tensor with the point cloud with shape (NUM_POINTS, 3).
            - A tensor with the label.
            - A tensor with the part labels with shape (NUM_POINTS,).
        """
        pcd = self.pcds[index]
        label = self.labels[index]
        part_labels = self.part_labels[index]

        pcd = self.transform(pcd)

        return pcd, label, part_labels

    @classmethod
    def color_pcd(cls, pcd: Tensor, part_labels: Tensor) -> o3d.geometry.PointCloud:
        """Prepare one item in order to be visualized using open3D draw geometries.

        Args:
            pcd: A tensor with the point cloud with shape (NUM_POINTS, 3).
            part_labels: A tensor with the labels for all the points with shape (NUM_POINTS,).

        Returns:
            The point cloud to draw with open 3D.
        """
        col = cls.part_colors[part_labels, :]

        return get_o3d_pcd_from_tensor(pcd, col)

    def get_class_name(self, label: int) -> str:
        """Get the class name from the class id.

        Args:
            label: The class numeric id.

        Returns:
            The class name.
        """
        return self.class_names[label]
