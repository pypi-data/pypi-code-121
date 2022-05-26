from dataclasses import dataclass, field
from enum import Enum


class RunProfile(Enum):
    ASAP = 'asap'
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'

    @staticmethod
    def parse(value):
        result = [member for name, member in RunProfile.__members__.items() if member.value.lower() == value.lower()]
        return result[0]


@dataclass
class ProcessRunProfile:
    market: str
    name: str
    run_profile: RunProfile = field(default=RunProfile.ASAP)
