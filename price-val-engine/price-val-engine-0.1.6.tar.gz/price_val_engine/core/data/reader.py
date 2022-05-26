import csv
from price_val_engine.core.data import FSObject

class BaseReader(FSObject):
    
    def read(self):
        raise NotImplemented("")


class CSVReader(BaseReader):
    
    def __init__(self, file_path, mode='rt', *args, **kwargs) -> None:
        super().__init__(file_path)
        self.args = args
        self.kwargs = kwargs
        self.mode = mode
            
    def read(self):
        filesystem = self.get_fs()
        with filesystem.open(self.file_path, self.mode) as fs:
            for row in csv.DictReader(fs, *self.args, **self.kwargs):
                yield row
            fs.close()
                    