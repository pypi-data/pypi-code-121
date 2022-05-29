from dataclasses import dataclass

@dataclass
class Address:
    """Class that holds address data returned by the provider"""
    address: str
    balance: str
    