import logging

from conductor.instrument.InstrumentExchangeHandler import InstrumentExchangeHandler
from conductor.provider.ExchangeDataProvider import ExchangeDataProvider
from conductor.transform.ExchangeTransformer import ExchangeTransformer


class ExchangeConductor:

    def __init__(self, options, transformer: ExchangeTransformer, data_provider: ExchangeDataProvider, handler: InstrumentExchangeHandler):
        self.log = logging.getLogger('ExchangeConductor')
        self.options = options
        self.transformer = transformer
        self.data_provider = data_provider
        self.handler = handler

    def get_instrument_exchanges(self):
        instrument_exchanges_holder = self.handler.obtain_holder()
        exchange_instruments_payload = self.data_provider.fetch_exchange_instruments()
        self.log.info(f'Fetched raw exchange instruments[{len(exchange_instruments_payload)}]')
        for exchange_instrument_data in exchange_instruments_payload:
            instrument_exchange = self.transformer.transform(exchange_instrument_data)
            if instrument_exchange is not None:
                self.log.debug(f'Adding transformed instrument exchange:{instrument_exchange}')
                instrument_exchanges_holder.add(instrument_exchange)
        self.handler.update_holder(instrument_exchanges_holder)
