from dataclasses import (
    dataclass,
    field,
)
from ..main import _base


@dataclass
class ApiAnswer(_base.AlphaDataclass):
    token_status: str = "success"
    status: str = "success"
    error: int = 0
    status_code: int = 200
    status_description: str = ""
    requester: str = "unknow"
    data: dict = field(default_factory=lambda: {})
