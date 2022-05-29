import numpy as np
import pytorch_lightning as pl
import torch
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from ..tools.logger import Logger
from .config import instantiate_from_config
import sys


class RandomSplitDataset(Dataset):
    def __init__(self, dataset: Dataset, random_split: float = 1.0) -> None:
        super().__init__()

        self.dataset = dataset
        self.random_split = random_split

        N = len(self.dataset)
        n = int(N * float(random_split))
        self.__index_list = np.random.permutation(N)[:n].tolist()

    def __len__(self):
        return len(self.__index_list)

    def __getitem__(self, index):
        real_index = self.__index_list[index]
        return self.dataset.__getitem__(real_index)


class LightningDataset(pl.LightningDataModule):
    def __init__(self, train=None, validation=None, test=None):
        super().__init__()
        self.configs = {
            "train": train,
            "validation": validation,
            "test": test,
        }
        if train is not None:
            self.train_dataloader = self._train_dataloader
        if validation is not None:
            self.val_dataloader = self.val_dataloader
        if test is not None:
            self.test_dataloader = self._test_dataloader

    def _train_dataloader(self):
        return self.__get_dataloader(self.configs["train"])
    
    def _val_dataloader(self):
        return self.__get_dataloader(self.configs["validation"])

    def _test_dataloader(self):
        return self.__get_dataloader(self.configs["test"])

    def __get_dataloader(self, config) -> DataLoader:
        random_split = float(config["random_split"])
        if not (0 < random_split <= 1.0):
            Logger.error("random_split: (0.0, 1.0]")
            sys.exit(0)

        dataset = instantiate_from_config(config)
        if random_split != 1.0:
            Logger.info(f"RandomSplitDataset, random_split:{random_split:.2f}")
            dataset = RandomSplitDataset(dataset, random_split=random_split)

        return DataLoader(dataset=dataset, **config["data_loader"])


def single_to_batch(data_dict):
    batch = dict()
    for key, value in data_dict.items():
        if isinstance(value, torch.FloatTensor):
            batch[key] = value.unsqueeze(0)
        elif isinstance(value, int):
            batch[key] = torch.LongTensor(value).unsqueeze(0)
        elif isinstance(value, np.ndarray):
            batch[key] = torch.from_numpy(value).unsqueeze(0)
        else:
            Logger.error(f"key:{key}, {type(value)}")
    return batch
