from enum import Enum
from typing import List

import nbformat
from pydantic import BaseModel


class ExecutionStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WAITING = "waiting"


class RunResult(BaseModel):
    status: ExecutionStatus
    cells: List[nbformat.NotebookNode]
