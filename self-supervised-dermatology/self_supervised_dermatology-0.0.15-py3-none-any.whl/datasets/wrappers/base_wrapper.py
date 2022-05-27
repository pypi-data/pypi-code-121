from torch.utils.data import Dataset
from abc import ABC
from abc import abstractmethod
from torchvision import transforms


class DatasetWrapper(ABC, Dataset):
    def __init__(self,
                 ds: Dataset,
                 debug=False):
        super().__init__()

        self.ds = ds
        self.debug = debug
        if debug:
            raise Warning('Dataset is in DEBUG mode')

        self.preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    @abstractmethod
    def __getitem_internal__(self, idx, preprocess=True):
        pass

    def __len__(self):
        return len(self.ds)

    def __getitem__(self, idx):
        return self.__getitem_internal__(idx, True)

    def raw(self, idx):
        return self.__getitem_internal__(idx, False)
