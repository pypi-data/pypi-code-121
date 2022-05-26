from dataclasses import dataclass
from typing import List
from mlplatform_lib.dataclass import DataObjectOutCol

# example
# "name": "TEST",
# "sourceTableName": "TEST",
# "subtype": "Table",
# "outCols": [
#     {
#         "name": "C1"
#     },
#     {
#         "name": "C2"
#     }
# ],
# "shareRelation": [
# ]


@dataclass
class DataObject:
    id: str
    name: str
    out_cols: List[DataObjectOutCol]
    share_relation: List[str]
    source_table_name: str
    subtype: str
    author: str
    description: str
    created_on: str
    last_edited: str
