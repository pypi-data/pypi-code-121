from dataclasses import dataclass
from typing import Optional

@dataclass
class Block:
    """Class that holds block data returned by the provider"""
    id: str
    miner: str
    difficulty: str
    timestamp: str
    raw_data: Optional[str] = "None"