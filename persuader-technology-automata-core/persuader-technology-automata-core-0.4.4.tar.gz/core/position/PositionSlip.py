from dataclasses import dataclass, field
from enum import Enum

from core.number.BigFloat import BigFloat


class Status(Enum):
    NEW = 'new'
    USED = 'used'


@dataclass
class PositionSlip:
    instrument: str
    quantity: BigFloat
    status: Status = field(default=Status.NEW)
