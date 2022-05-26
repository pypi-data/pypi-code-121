import csv
from io import StringIO
import fsspec
from price_val_engine.conf import settings
from price_val_engine.core.data import FSObject
import boto3


class BaseWriter(FSObject):
    
    def write(self):
        raise NotImplemented("")


class CSVWriter(BaseWriter):
    
    def __init__(self, file_path, mode='wt', storage_options=None, *args, **kwargs) -> None:
        super().__init__(file_path)
        self.args = args
        self.kwargs = kwargs
        self.mode = mode
        self.storage_options = storage_options or {}
        
    def write(self, items, headers):
        filesystem = self.get_fs()
        with filesystem.open(self.file_path, self.mode) as fs:
            writer = csv.DictWriter(fs, fieldnames=headers, *self.args, **self.kwargs)
            writer.writeheader()
            writer.writerows(items)
            fs.close()