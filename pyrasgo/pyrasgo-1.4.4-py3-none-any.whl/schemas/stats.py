from typing import Optional

from pydantic import BaseModel


class GenerateStat(BaseModel):
    dwTableId: int
    dimensionColumnId: Optional[int]
    onlyIfDataChanged: Optional[bool]
