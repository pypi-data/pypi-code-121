from abc import ABC
from typing import Any


class Command(ABC):
    def execute(self) -> Any:
        raise NotImplementedError("Method not implemented yet")
