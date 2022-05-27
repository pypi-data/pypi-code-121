import os
import torch
import random
import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Union
from glob import glob
from torchvision import transforms
from torchvision.transforms import functional as TF

from src.datasets.downstream.base_dataset import BaseDataset


class ISICTask1Dataset(BaseDataset):
    """ISIC Task 1 dataset."""
    IMG_COL = 'img_path'
    LBL_COL = 'mask_path'

    def __init__(self,
                 dataset_dir: Union[str, Path] = 'data/ISIC_Task1/',
                 dataset_type: str = 'train'):
        """
        Initializes the dataset.

        Sets the correct path for the needed arguments.

        Parameters
        ----------
        csv_file : str
            Path to the csv file with metadata, including annotations.
        dataset_dir : str
            Directory with all the images.
        """
        super().__init__(transform=None, val_transform=None)
        # check if the dataset path exists
        self.dataset_dir = Path(dataset_dir)
        if not self.dataset_dir.exists():
            raise ValueError(
                f'Image path must exist, path: {self.dataset_dir}')
        # check dataset type
        if dataset_type not in ['train', 'val']:
            raise ValueError(f'Unknown dataset type: {dataset_type}')

        # create dicts for retreiving imgs and masks
        imgs_path_dict = {
            os.path.splitext(os.path.basename(x))[0]: x
            for x in glob(os.path.join(dataset_dir, dataset_type, '*', '*.jpg'))
        }
        masks_path_dict = {
            os.path.splitext(os.path.basename(x))[0]: x
            for x in glob(os.path.join(dataset_dir, dataset_type, '*', '*.png'))
        }

        # create the metadata dataframe
        self.meta_data = pd.DataFrame()
        for key, item in imgs_path_dict.items():
            mask_path = masks_path_dict.get(f'{key}_segmentation')
            s_item = pd.Series([key, item, mask_path])
            self.meta_data = self.meta_data.append(s_item, ignore_index=True)
        self.meta_data.columns = ['img_name', 'img_path', 'mask_path']
        # configs
        self.n_classes = 1

    def _transform(self, image, mask):
        # Resize
        resize = transforms.Resize(size=(256, 256))
        image = resize(image)
        mask = resize(mask)

        # Random crop
        i, j, h, w = transforms.RandomCrop.get_params(
            image, output_size=(224, 224))
        image = TF.crop(image, i, j, h, w)
        mask = TF.crop(mask, i, j, h, w)

        # Random horizontal flipping
        if random.random() > 0.5:
            image = TF.hflip(image)
            mask = TF.hflip(mask)

        # Random vertical flipping
        if random.random() > 0.5:
            image = TF.vflip(image)
            mask = TF.vflip(mask)

        # Transform to tensor
        image = TF.to_tensor(image)
        mask = TF.to_tensor(mask)
        return image, mask

    def _val_transform(self, image, mask):
        # Resize
        resize = transforms.Resize(size=(224, 224))
        image = resize(image)
        mask = resize(mask)

        # Transform to tensor
        image = TF.to_tensor(image)
        mask = TF.to_tensor(mask)
        return image, mask

    def __len__(self):
        return len(self.meta_data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = self.meta_data.iloc[idx][self.IMG_COL]
        image = Image.open(img_name)
        image = image.convert('RGB')

        mask_path = self.meta_data.iloc[idx][self.LBL_COL]
        mask = Image.open(mask_path)
        mask = mask.convert('L')

        if self.training:
            image, mask = self._transform(image, mask)
        else:
            image, mask = self._val_transform(image, mask)
        return image, mask
