from typing import List
from dataclasses import dataclass
from mlplatform_lib.dataclass import ColumnOption, RowOption


@dataclass
class SelectorProperty:
    column_select_options: List[ColumnOption]
    row_select_options: List[RowOption]
