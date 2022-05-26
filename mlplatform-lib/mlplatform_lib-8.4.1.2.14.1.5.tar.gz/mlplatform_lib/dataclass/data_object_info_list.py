from dataclasses import dataclass
from typing import List
from mlplatform_lib.dataclass import DataObject


@dataclass
class DataObjectInfoList:
    data_object_info_list: List[DataObject]
