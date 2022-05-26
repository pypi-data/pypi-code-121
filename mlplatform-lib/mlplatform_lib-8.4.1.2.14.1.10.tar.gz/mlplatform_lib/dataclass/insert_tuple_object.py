from dataclasses import dataclass
from typing import List


@dataclass
class InsertTupleObject:
    isTruncated: bool
    targetColNames: List[str]
    tableData: List[List[str]]
