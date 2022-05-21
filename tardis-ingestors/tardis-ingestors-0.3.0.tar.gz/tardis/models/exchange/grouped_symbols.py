from enum import Enum


class GroupedSymbol(Enum):
    """
    Special grouped symbols that gather info from all other exchange symbols.
    """

    SPOT = "SPOT"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    PERPETUALS = "PERPETUALS"
