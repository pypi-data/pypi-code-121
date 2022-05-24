from typing import List, TypedDict
from typing_extensions import NotRequired


class Log(TypedDict, total=False):
    address: str
    block_number: int
    data: str
    gas_price: NotRequired[int]
    gas_used: NotRequired[int]
    log_index: int
    timestamp: NotRequired[int]
    topics: List[str]
    transaction_hash: str
    transaction_index: int