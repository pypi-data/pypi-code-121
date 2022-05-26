from dataclasses import dataclass
from mlplatform_lib.dataclass import TableColumnInfo
from typing import List

# "colInfoList": [
#     {
#         "name": "review",
#         "type": "VARCHAR",
#         "alias": "review",
#         "nullable": true,
#         "primaryKey": false,
#         "foreignKey": false,
#         "description": ""
#     },
#     {
#         "name": "sentiment",
#         "type": "VARCHAR",
#         "alias": "sentiment",
#         "nullable": true,
#         "primaryKey": false,
#         "foreignKey": false,
#         "description": ""
#     },
#     {
#         "name": "id",
#         "type": "VARCHAR",
#         "alias": "id",
#         "nullable": true,
#         "primaryKey": false,
#         "foreignKey": false,
#         "description": ""
#     }
# ],
# "numRows": 0


@dataclass
class TableDescInfo:
    col_info_list: List[TableColumnInfo]
    numRows: int = 0
