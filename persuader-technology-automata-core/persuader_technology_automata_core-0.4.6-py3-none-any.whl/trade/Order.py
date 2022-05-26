from dataclasses import dataclass, field
from enum import Enum

from core.number.BigFloat import BigFloat


class Status(Enum):
    NEW = 'new'
    CANCELLED = 'cancelled'
    EXECUTED = 'executed'
    ERROR = 'error'

    @staticmethod
    def parse(value):
        result = [member for name, member in Status.__members__.items() if member.value.lower() == value.lower()]
        return result[0]


class OrderType(Enum):
    LIMIT = 'limit'
    MARKET = 'market'

    @staticmethod
    def parse(value):
        result = [member for name, member in OrderType.__members__.items() if member.value.lower() == value.lower()]
        return result[0]


@dataclass
class Order:
    instrument_from: str
    instrument_to: str
    quantity: BigFloat
    order_id: str
    order_type: OrderType
    status: Status
    instant: int
    price: BigFloat = field(default=None)
    value: BigFloat = field(default=None)
