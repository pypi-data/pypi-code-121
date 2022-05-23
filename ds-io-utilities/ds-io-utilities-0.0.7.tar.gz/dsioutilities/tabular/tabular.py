from ..dataset import Dataset
import importlib
import os


class TabularDataset(Dataset):
    dataset_type = os.path.basename(__file__).split('.py')[0]

    def __init__(self, name, dataset_type=None):
        super().__init__(name, dataset_type)

    def get_path(self):
        storage_type = super().get_storage_type().lower()
        get_path = importlib.import_module("." + storage_type, package="dsioutilities.tabular").get_path
        return get_path(self.name)

