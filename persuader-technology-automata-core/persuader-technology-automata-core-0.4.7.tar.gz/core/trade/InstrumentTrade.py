from dataclasses import dataclass, field
from enum import Enum

from core.number.BigFloat import BigFloat


class Status(Enum):
    NEW = 'new'
    SUBMITTED = 'submitted'
    CANCELLED = 'cancelled'
    EXECUTED = 'executed'
    ERROR = 'error'

    @staticmethod
    def parse(value):
        result = [member for name, member in Status.__members__.items() if member.value.lower() == value.lower()]
        return result[0]


class TradeMode(Enum):
    TRADE = 'trade'
    PREDICT = 'predict'

    @staticmethod
    def parse(value):
        result = [member for name, member in TradeMode.__members__.items() if member.value.lower() == value.lower()]
        return result[0]


@dataclass
class InstrumentTrade:
    instrument_from: str
    instrument_to: str
    quantity: BigFloat
    price: BigFloat = field(default=None)
    value: BigFloat = field(default=None)
    status: Status = field(default=Status.NEW)
    description: str = field(default=None)
    order_id: str = field(default=None)
    instant: int = field(default=None)
    mode: TradeMode = field(default=TradeMode.TRADE)

    def __eq__(self, other):
        return f'{self.instrument_from}{self.instrument_to}{self.status.value}{self.order_id}' == f'{other.instrument_from}{other.instrument_to}{other.status.value}{other.order_id}'
