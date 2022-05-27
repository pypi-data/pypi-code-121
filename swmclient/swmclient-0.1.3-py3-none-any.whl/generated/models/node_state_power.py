from enum import Enum


class NodeStatePower(str, Enum):
    UP = "up"
    DOWN = "down"

    def __str__(self) -> str:
        return str(self.value)
