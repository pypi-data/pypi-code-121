from dataclasses import dataclass

@dataclass
class Summary:
    """Class that holds summary data of a blockchain returned by the provider"""
    name: str
    price: str
    market_cap: str
    total_supply: str