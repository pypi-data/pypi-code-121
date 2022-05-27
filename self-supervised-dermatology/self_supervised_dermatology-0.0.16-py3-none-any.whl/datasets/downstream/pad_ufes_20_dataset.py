import os
import torch
import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Union

from src.datasets.downstream.base_dataset import BaseDataset


class PADUFES20Dataset(BaseDataset):
    """PAD-UFES-20 dataset."""
    IMG_COL = 'img_id'
    LBL_COL = 'diagnostic'

    def __init__(self,
                 csv_file: Union[str, Path] = 'data/PAD-UFES-20/metadata.csv',
                 root_dir: Union[str, Path] = 'data/PAD-UFES-20/images/',
                 transform=None,
                 val_transform=None):
        """
        Initializes the dataset.

        Sets the correct path for the needed arguments.

        Parameters
        ----------
        csv_file : str
            Path to the csv file with metadata, including annotations.
        root_dir : str
            Directory with all the images.
        transform : Union[callable, optional]
            Optional transform to be applied to the images.
        """
        super().__init__(transform=transform, val_transform=val_transform)
        # check if the dataset path exists
        self.csv_file = Path(csv_file)
        if not self.csv_file.exists():
            raise ValueError(
                f'CSV metadata path must exist, path: {self.csv_file}')
        self.root_dir = Path(root_dir)
        if not self.root_dir.exists():
            raise ValueError(
                f'Image path must exist, path: {self.root_dir}')

        # load the metadata and encode the label
        self.meta_data = pd.DataFrame(pd.read_csv(self.csv_file))
        self.meta_data[self.LBL_COL] = self.labelencoder.fit_transform(
            self.meta_data[self.LBL_COL])
        self.classes = self.labelencoder.classes_
        self.n_classes = len(self.classes)

    def __len__(self):
        return len(self.meta_data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.meta_data.loc[self.meta_data.index[idx], self.IMG_COL]
        img_name = os.path.join(self.root_dir, img_path)
        image = Image.open(img_name)
        image = image.convert('RGB')
        if self.transform and self.training:
            image = self.transform(image)
        elif self.val_transform and not self.training:
            image = self.val_transform(image)

        diagnosis = self.meta_data.loc[self.meta_data.index[idx], self.LBL_COL]
        return image, int(diagnosis)
