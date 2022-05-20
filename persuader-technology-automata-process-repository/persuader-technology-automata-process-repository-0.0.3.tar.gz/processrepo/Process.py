from dataclasses import dataclass, field
from enum import Enum


class ProcessStatus(Enum):
    UNKNOWN = 'unknown'
    RUNNING = 'running'
    ERROR = 'error'
    STOPPED = 'stopped'

    @staticmethod
    def parse(value):
        result = [member for name, member in ProcessStatus.__members__.items() if member.value.lower() == value.lower()]
        return result[0]


@dataclass
class Process:
    market: str
    name: str
    instant: int
    status: ProcessStatus = field(default=ProcessStatus.UNKNOWN)
