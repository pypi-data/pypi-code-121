from enum import Enum


class NodeStateAlloc(str, Enum):
    IDLE = "idle"
    STOPPED = "stopped"
    OFFLINE = "offline"
    BUSY = "busy"

    def __str__(self) -> str:
        return str(self.value)
