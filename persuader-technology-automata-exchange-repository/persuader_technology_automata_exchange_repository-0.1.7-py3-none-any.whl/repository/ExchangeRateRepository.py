import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.exchange.ExchangeRate import ExchangeRate
from core.exchange.InstrumentExchange import InstrumentExchange
from core.options.exception.MissingOptionError import MissingOptionError
from exchange.rate.ExchangeRateHolder import ExchangeRateHolder

EXCHANGE_RATE_TIMESERIES_KEY = 'EXCHANGE_RATE_TIMESERIES_KEY'
EXCHANGE_RATE_TIMESERIES_RETENTION = 'EXCHANGE_RATE_TIMESERIES_RETENTION'


class ExchangeRateRepository:

    def __init__(self, options):
        self.log = logging.getLogger('ExchangeRateRepository')
        self.options = options
        self.__check_options()
        self.timeseries_key = options[EXCHANGE_RATE_TIMESERIES_KEY]
        self.timeseries_retention_time = options[EXCHANGE_RATE_TIMESERIES_RETENTION]
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options [{EXCHANGE_RATE_TIMESERIES_KEY}, {EXCHANGE_RATE_TIMESERIES_RETENTION}]')
            raise MissingOptionError(f'missing option please provide options [{EXCHANGE_RATE_TIMESERIES_KEY}, {EXCHANGE_RATE_TIMESERIES_RETENTION}]')
        if EXCHANGE_RATE_TIMESERIES_KEY not in self.options:
            self.log.warning(f'missing option please provide option {EXCHANGE_RATE_TIMESERIES_KEY}')
            raise MissingOptionError(f'missing option please provide option {EXCHANGE_RATE_TIMESERIES_KEY}')
        if EXCHANGE_RATE_TIMESERIES_RETENTION not in self.options:
            self.log.warning(f'missing option please provide option {EXCHANGE_RATE_TIMESERIES_RETENTION}')
            raise MissingOptionError(f'missing option please provide option {EXCHANGE_RATE_TIMESERIES_RETENTION}')

    def instrument_exchange_timeseries_key(self, instrument_exchange: InstrumentExchange):
        instruments_to_exchange = f'{instrument_exchange.instrument}/{instrument_exchange.to_instrument}'
        return self.timeseries_key.format(instruments_to_exchange)

    def store(self, exchange_rate: ExchangeRate, event_time):
        rate_timeseries_key = self.instrument_exchange_timeseries_key(exchange_rate)
        self.cache.create_timeseries(rate_timeseries_key, 'rate', double_precision=True, limit_retention=self.timeseries_retention_time)
        self.cache.add_to_timeseries(rate_timeseries_key, event_time, exchange_rate.rate)

    def retrieve(self, instrument_exchange: InstrumentExchange, time_from, time_to='+', exchange_rate_holder: ExchangeRateHolder = ExchangeRateHolder()) -> ExchangeRateHolder:
        rate_timeseries_key = self.instrument_exchange_timeseries_key(instrument_exchange)
        if self.cache.does_timeseries_exist(rate_timeseries_key):
            timeseries_data = self.cache.get_timeseries_data(rate_timeseries_key, time_from=time_from, time_to=time_to, double_precision=True, reverse_direction=True)
            for rate, value in timeseries_data:
                exchange_rate = ExchangeRate(instrument_exchange.instrument, instrument_exchange.to_instrument, value)
                exchange_rate_holder.add(exchange_rate, rate)
        return exchange_rate_holder

    def retrieve_multiple(self, instrument_exchanges: List[InstrumentExchange], time_from, time_to='+') -> ExchangeRateHolder:
        exchange_rate_holder = ExchangeRateHolder()
        for instrument_exchange in instrument_exchanges:
            self.retrieve(instrument_exchange, time_from, time_to, exchange_rate_holder)
        return exchange_rate_holder
