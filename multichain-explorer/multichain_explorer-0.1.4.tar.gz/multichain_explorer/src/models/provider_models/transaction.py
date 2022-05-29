from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    """Class that holds transaction data returned by the provider"""
    id: str
    address_from: str
    address_to: str
    value: str
    block: str
    raw_data: Optional[str] = None
    