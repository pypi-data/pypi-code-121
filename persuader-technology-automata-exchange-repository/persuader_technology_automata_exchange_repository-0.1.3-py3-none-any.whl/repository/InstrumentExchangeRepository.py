import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.exchange.InstrumentExchange import InstrumentExchange
from core.options.exception.MissingOptionError import MissingOptionError
from exchange.InstrumentExchangesHolder import InstrumentExchangesHolder

INSTRUMENT_EXCHANGES_KEY = 'INSTRUMENT_EXCHANGES_KEY'


class InstrumentExchangeRepository:

    def __init__(self, options):
        self.log = logging.getLogger('InstrumentExchangeRepository')
        self.options = options
        self.__check_options()
        self.instrument_exchanges_key = options[INSTRUMENT_EXCHANGES_KEY]
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'Instrument Exchange Repository missing option please provide options {INSTRUMENT_EXCHANGES_KEY}')
            raise MissingOptionError(f'Instrument Exchange Repository missing option please provide options {INSTRUMENT_EXCHANGES_KEY}')
        if INSTRUMENT_EXCHANGES_KEY not in self.options:
            self.log.warning(f'Instrument Exchange Repository missing option please provide option {INSTRUMENT_EXCHANGES_KEY}')
            raise MissingOptionError(f'Instrument Exchange Repository missing option please provide option {INSTRUMENT_EXCHANGES_KEY}')

    def store(self, instrument_exchanges: InstrumentExchangesHolder):
        key = self.options[INSTRUMENT_EXCHANGES_KEY]
        all_exchanges = instrument_exchanges.get_all()
        serialized = list([[ie.instrument, ie.to_instrument] for ie in all_exchanges])
        self.cache.store(key, serialized)

    def retrieve(self) -> InstrumentExchangesHolder:
        key = self.options[INSTRUMENT_EXCHANGES_KEY]
        serialized = self.cache.fetch(key, as_type=list)
        holder = InstrumentExchangesHolder()
        for serialized_instrument_exchange in serialized:
            (instrument, to_instrument) = tuple(serialized_instrument_exchange)
            holder.add(InstrumentExchange(instrument, to_instrument))
        return holder
