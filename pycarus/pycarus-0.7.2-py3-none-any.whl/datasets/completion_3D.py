import shutil
from pathlib import Path
from typing import Callable, List, Tuple

import h5py  # type: ignore
import numpy as np
import open3d  # type: ignore
import torch
from torch.utils.data import Dataset

from pycarus.geometry.pcd import get_o3d_pcd_from_tensor
from pycarus.transforms.var import Compose
from pycarus.utils import download_and_extract

T_ITEM = Tuple[str, str, torch.Tensor, torch.Tensor]


class Completion3D(Dataset):
    def __init__(
        self,
        root: Path,
        split: str,
        categories: List[str] = [],
        download: bool = False,
        transforms_complete: List[Callable] = [],
        transforms_incomplete: List[Callable] = [],
        transforms_all: List[Callable] = [],
    ) -> None:
        """Class implementing the Completion3D dataset as proposed in:

        Tchapmi, L. P., Kosaraju, V., Rezatofighi, H., Reid, I., & Savarese, S. (2019).
        Topnet: Structural point cloud decoder.
        In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 383-392).

        Args:
            root: The path to the folder containing the dataset.
            split: The name of the split to load.
            categories: A list of categories id to select. Defaults to [].
            download: If True download the dataset using the "tmp" folder. Defaults to False.
            transforms_complete: The transform to apply to the complete cloud. Defaults to [].
            transforms_incomplete: The transform to apply to the incomplete cloud. Defaults to [].
            transforms_all: The transform to apply to both the complete
                            and the incomplete cloud. Defaults to [].

        Raises:
            FileNotFoundError: If the folder does not exist.
            ValueError: If the chosen split is not allowed.
        """
        super().__init__()

        self.split = split
        self.splits = ["train", "val", "test"]
        if self.split not in self.splits:
            raise ValueError(f"{self.split} value not allowed, only allowed {self.splits}.")
        if self.split == "test":
            print("Careful: complete clouds are not available for the test split!")

        self.root = root
        if not download and not self.root.is_dir():
            raise FileNotFoundError(f"{self.root} not found.")

        self.transform_complete = Compose(transforms_complete)
        self.transform_incomplete = Compose(transforms_incomplete)
        self.transform_all = Compose(transforms_all)

        if download:
            if self.root.exists():
                print("Dataset root already exists, not downloading.")
            else:
                self.url = "http://download.cs.stanford.edu/downloads/completion3d/dataset2019.zip"
                self.__download()

        self.list_file, cat_in_file = self.read_samples(
            self.root / f"{self.split}.list", categories
        )
        self.categories = categories if categories else cat_in_file

    def __getitem__(self, index: int) -> T_ITEM:
        sample = self.list_file[index]
        id_category, name = sample.split("/")[0], sample.split("/")[1]

        path_incomplete = self.root / self.split / "partial" / id_category / f"{name}.h5"
        incomplete_np = np.array(h5py.File(path_incomplete, "r")["data"])
        incomplete = torch.tensor(incomplete_np, dtype=torch.float)

        if self.split == "test":
            complete = torch.zeros_like(incomplete)
        else:
            path_complete = self.root / self.split / "gt" / id_category / f"{name}.h5"
            complete_np = np.array(h5py.File(path_complete, "r")["data"])
            complete = torch.tensor(complete_np, dtype=torch.float)

        complete = self.transform_all(self.transform_complete(complete))
        incomplete = self.transform_all(self.transform_incomplete(incomplete))

        return id_category, name, incomplete, complete

    def __len__(self) -> int:
        return len(self.list_file)

    @staticmethod
    def read_samples(path: Path, filter_categories: List[str]) -> Tuple[List[str], List[str]]:
        """Read a text file.

        Args:
            path: the path to the file to read.

        Returns:
            A tuple containing:
            - The list with one line of the file as sample.
            - The list of categories.
        """
        list_files: List[str] = []
        list_categories: List[str] = []
        with open(path, "rt") as f:
            for line in f.readlines():
                name_sample = line.rstrip()
                category = name_sample.split("/")[0]
                if category not in list_categories:
                    list_categories.append(category)

                if filter_categories:
                    if category in filter_categories:
                        list_files.append(name_sample)
                else:
                    list_files.append(name_sample)

        return list_files, list_categories

    def __download(self) -> None:
        """Function to download the dataset."""
        path_temp = Path("/tmp")
        path_file_downloaded = path_temp / Path(self.url.split("/")[-1])
        download_and_extract(self.url, path_file_downloaded, path_temp, None)

        path_ds_extracted = path_temp / "shapenet"

        shutil.copytree(str(path_ds_extracted), self.root)
        shutil.rmtree(str(path_ds_extracted))

    @classmethod
    def show_item(cls, sample: T_ITEM) -> open3d.geometry.PointCloud:
        """Prepare one item in order to be visualized using open3D draw geometries.
        Args:
            sample: The sample to show.
        Returns:
            The point cloud to draw with open 3D.
        """
        _, _, incomplete, complete = sample
        pcd_incomplete = get_o3d_pcd_from_tensor(incomplete)

        complete = complete + torch.tensor([1.0, 0.0, 0.0])
        pcd_complete = get_o3d_pcd_from_tensor(complete)

        return pcd_complete + pcd_incomplete

    def get_categories(self) -> List[str]:
        """Get the list of loaded categories.

        Returns:
            A list containing the ids of the loaded categories.
        """
        return self.categories
