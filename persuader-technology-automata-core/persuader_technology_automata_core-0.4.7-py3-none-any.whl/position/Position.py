from dataclasses import dataclass

from core.number.BigFloat import BigFloat


@dataclass
class Position:
    instrument: str
    quantity: BigFloat
    instant: int
    exchanged_from: str = None

    def __eq__(self, other):
        return f'{self.instrument}{self.exchanged_from}{str(self.instant)}' == f'{other.instrument}{other.exchanged_from}{str(other.instant)}'
