from torch.utils.data import Dataset
from ..tools.logger import Logger


class MixedDataset(Dataset):
    def __init__(self, dataset_list):
        self.dataset_list = dataset_list
        self.lens = [len(dataset) for dataset in dataset_list]
        total = sum(self.lens)
        Logger.info(f"mixed dataset-> total={total}, lens: {self.lens}")

    def __getitem__(self, index):
        k = index
        for i, len in enumerate(self.lens):
            if k < len:
                return self.dataset_list[i][k]
            k -= len

    def __len__(self):
        return sum(self.lens)
