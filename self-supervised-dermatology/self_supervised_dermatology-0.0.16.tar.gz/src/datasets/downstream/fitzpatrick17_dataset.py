import os
import torch
import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Union
from glob import glob

from src.datasets.downstream.base_dataset import BaseDataset


class Fitzpatrick17kDataset(BaseDataset):
    """Fitzpatrick17k dataset."""
    IMG_COL = 'path'
    LBL_COL = 'lbl_high'

    def __init__(self,
                 csv_file: Union[str, Path] = 'data/fitzpatrick17k/fitzpatrick17k.csv',
                 dataset_dir: Union[str, Path] = 'data/fitzpatrick17k/',
                 transform=None,
                 val_transform=None,
                 return_fitzpatrick=False):
        """
        Initializes the dataset.

        Sets the correct path for the needed arguments.

        Parameters
        ----------
        csv_file : str
            Path to the csv file with metadata, including annotations.
        dataset_dir : str
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
        self.dataset_dir = Path(dataset_dir)
        if not self.dataset_dir.exists():
            raise ValueError(
                f'Image path must exist, path: {self.dataset_dir}')
        # transform the dataframe for better loading
        imageid_path_dict = {
            os.path.splitext(os.path.basename(x))[0]: x
            for x in glob(os.path.join(self.dataset_dir, '*', '*.jpg'))
        }

        # load the metadata
        self.meta_data = pd.DataFrame(pd.read_csv(csv_file))
        self.meta_data['path'] = self.meta_data['md5hash'].map(imageid_path_dict.get)
        self.meta_data['lbl_low'] = self.meta_data['label'].astype('category').cat.codes
        self.meta_data['lbl_mid'] = self.meta_data['nine_partition_label'].astype('category').cat.codes
        self.meta_data['lbl_high'] = self.meta_data['three_partition_label'].astype('category').cat.codes

        # global configs
        self.return_fitzpatrick = return_fitzpatrick
        self.classes = self.meta_data['three_partition_label'].unique().tolist()
        self.n_classes = len(self.classes)

    def __len__(self):
        return len(self.meta_data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.meta_data.loc[self.meta_data.index[idx], self.IMG_COL]
        image = Image.open(img_path)
        image = image.convert('RGB')
        if self.transform and self.training:
            image = self.transform(image)
        elif self.val_transform and not self.training:
            image = self.val_transform(image)

        diagnosis = self.meta_data.loc[self.meta_data.index[idx], self.LBL_COL]
        if self.return_fitzpatrick:
            return image, int(self.meta_data.loc[self.meta_data.index[idx],
                                                 'fitzpatrick'])
        return image, int(diagnosis)
