from typing import Optional

from pydantic import BaseModel


class Kernel(BaseModel):
    """Kernel model."""

    id: str
    name: str
    last_activity: str
    execution_state: str
    connections: int


class Notebook(BaseModel):
    """Notebook model."""

    path: Optional[str] = None
    name: str


class Session(BaseModel):
    """Session model."""

    id: str
    path: str
    name: str
    type: str
    kernel: Kernel
    notebook: Notebook


class KernelName(BaseModel):
    """Kernel name scheme."""

    name: str = "python3"


class CreateSession(BaseModel):
    """Session scheme."""

    kernel: KernelName = KernelName()
    name: str
    path: str
    type: str = "notebook"
