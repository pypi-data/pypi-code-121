from enum import Enum

class SymbolType(Enum):
    spot= "spot"
    future = "future"
    option = "option"
    perpetual = "perpetual"