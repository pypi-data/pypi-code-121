import pandas as pd
from ..models.config import AlphaConfig

class AlphaExcel():
    file_raw    = None
    file_sheets = None

    def __init__(self,config=None,config_name=None):
        self.config = config
        if config_name is not None:
            self.config = AlphaConfig(config_name)

    def read_file(self,name=None,file_path=None):
        if name is not None and self.config is not None:
            if self.config.isPath(['files',name]):
                file_config   = self.config.get(['files',name])
                file_path     = file_config['file_path']
                
        self.file_raw       = pd.ExcelFile(file_path)

        self.file_sheets    = {sheet_name: self.file_raw.parse(sheet_name) 
                for sheet_name in self.file_raw.sheet_names}

    def get_sheets(self):
        return list(self.file_sheets.keys())

    def get_sheet(self,sheet_name=None, sheet_number=None,start_line=0):
        if sheet_name is not None:
            if sheet_name in self.file_sheets:
                return self.file_sheets[sheet_name]
        if sheet_number is not None:
            if len(self.file_sheets) >= sheet_number:
                return self.file_sheets[list(self.file_sheets.keys())[sheet_number]]