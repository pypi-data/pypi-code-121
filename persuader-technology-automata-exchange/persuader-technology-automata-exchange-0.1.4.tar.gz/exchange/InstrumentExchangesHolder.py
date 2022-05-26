from core.exchange.InstrumentExchange import InstrumentExchange


class InstrumentExchangesHolder:

    def __init__(self):
        self.exchanges = {}

    def add(self, instrument_exchange: InstrumentExchange):
        (instrument, to_instrument) = instrument_exchange
        if instrument not in self.exchanges:
            self.exchanges[instrument] = [to_instrument]
        else:
            instrument_exchanges = self.exchanges[instrument]
            if to_instrument not in instrument_exchanges:
                instrument_exchanges.append(to_instrument)

    def get(self, instrument):
        if instrument not in self.exchanges:
            return None
        return list([InstrumentExchange(k, vi) for k, v in self.exchanges.items() if k == instrument for vi in v])

    def get_all(self):
        return list([InstrumentExchange(k, vi) for k, v in self.exchanges.items() for vi in v])
