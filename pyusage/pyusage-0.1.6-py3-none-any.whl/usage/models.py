from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Error(BaseModel):

    traceback: str
    line: int
    module: str
    type: str


class Call(BaseModel):

    error: Optional[Error] = None


class Function(BaseModel):

    name: str
    labels: Optional[List[str]] = None
    calls: Optional[List[Call]] = None


class Session(BaseModel):

    functions: List[Function]
    timestamp: datetime
    metadata: Optional[Dict[str, str]] = None
