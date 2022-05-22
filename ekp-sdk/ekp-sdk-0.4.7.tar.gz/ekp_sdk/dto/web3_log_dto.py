from typing import List, TypedDict


class Web3LogDto(TypedDict, total=False):
    blockNumber: int
    blockHash: str
    removed: bool
    transactionLogIndex: int
    address: str
    data: str
    topics: List[str]
    transactionHash: str
    transactionIndex: int
    logIndex: int
