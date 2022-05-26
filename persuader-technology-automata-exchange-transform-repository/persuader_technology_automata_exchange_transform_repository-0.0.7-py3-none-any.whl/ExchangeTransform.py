from dataclasses import dataclass

from core.transform.Ignore import Ignore


@dataclass
class ExchangeTransform(Ignore):
    instrument: str
    transform: dict = None

    def __eq__(self, other):
        return self.instrument == other.instrument
