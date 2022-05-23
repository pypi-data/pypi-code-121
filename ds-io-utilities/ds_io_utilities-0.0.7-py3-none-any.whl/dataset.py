from abc import ABC, abstractmethod
from .utils import input_or_output, get_dataset_property


class Dataset(ABC):

    def __new__(cls, *args, **kw):
        
        
        if 'dataset_type' in kw:
            dataset_type = kw['dataset_type'].lower()
        elif len(args) > 0:
            dataset_type = args[1]
        else:
            dataset_type = "tabular"

        # Create a map of all subclasses based on dataset_type property (present on each subclass)
        subclass_map = {subclass.dataset_type: subclass for subclass in cls.__subclasses__()}


        # Select the proper subclass based on
        subclass = subclass_map[dataset_type]
        instance = super(Dataset, subclass).__new__(subclass)
        return instance
    
    def __init__(self, name, dataset_type = None):
        self.name = name
        self.direction = input_or_output(self.name)
        super().__init__()

    @abstractmethod
    def get_path(self, local_path, remote_path):
        pass

    def get_storage_type(self):
        return get_dataset_property(name=self.name, prop="dataStorageType")
