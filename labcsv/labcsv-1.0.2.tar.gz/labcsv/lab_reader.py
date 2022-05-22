import numpy as np
from enum import Enum
from typing import Union
import pandas as pd
import json
def read_csv(path:str):
    """read lab.csv

    Args:
        path : file path

    Returns:
        LabReader
    """
    return LabReader(pd.read_csv(path))

class DefaultHeaderName(Enum):
    """
    the first line names (default name only)
    """
    SENDER = "sender"
    SENDER_TYPE = "sender_type"
    SENDER_ID = "sender_id"
    TIMESTAMP = "timestamp"
    META = "meta"
    DURATION = "duration"
    ENDED_ON = "ended_on"
    RESPONSE = "response"
    TIME_COMMIT = "time_commit"
    TIME_END = "time_end"
    TIME_RENDER = "time_render"
    TIME_RUN = "time_run"
    TIME_SHOW = "time_show"
    TIME_SWITCH = "time_switch"
    URL = "url"

DefaultHeaderNameOrStr = Union[DefaultHeaderName,str]
class LabReader:
    
    def __init__(self,pd_data:pd.DataFrame):
        """
        Args:
            pd_data (pd.DataFrame): pandas dataframe
        """
        self.pandas_data =pd_data
        self.header_names = pd_data.columns.to_list()

    def get_column_values(self,header_names:Union[list[DefaultHeaderNameOrStr],str]):
        def _get_column_values(header_name:DefaultHeaderNameOrStr):
            if isinstance(header_name,DefaultHeaderName):
                header_name = header_name.value
            idx = self.header_names.index(header_name)
            return self.pandas_data.values[:,idx]
        if isinstance(header_names,list):
            columns = None
            for hname in header_names:
                if columns is None:
                    columns = _get_column_values(hname)
                else:
                    columns = np.vstack((columns,_get_column_values(hname)))
            return columns.transpose()
        else:
            return _get_column_values(header_names).transpose()
    
    def get_meta(self):
        meta = self.get_column_values(DefaultHeaderName.META)[0]
        return json.loads(meta)
