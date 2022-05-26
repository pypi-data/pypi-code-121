from dataclasses import dataclass


@dataclass
class InstrumentExchange:
    instrument: str
    to_instrument: str

    def __iter__(self):
        return iter((self.instrument, self.to_instrument))
