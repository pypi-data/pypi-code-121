from dataclasses import dataclass


@dataclass
class TradeTransform:
    trade: str
    transform: dict = None

    def __eq__(self, other):
        return self.trade == other.trade
