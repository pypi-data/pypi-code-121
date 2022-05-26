from dataclasses import dataclass
from .column_of_table_from_default_source import ColumnOfTableFromDefaultSource
from typing import List


@dataclass
class TableFromDefaultDataSourceInfo:
    table_name: str
    column_list: List[ColumnOfTableFromDefaultSource]
