import logging

import ccxt
from ccxt.base.exchange import Exchange

# from notecoin.base.database import KlineData
# data = KlineData()
# values = [
#     {'source': 'okex', 'symbol': 'a', 'timestamp': '34'},
#     {'source': 'okex', 'symbol': 'a', 'timestamp': '35'},
#     {'source': 'okex', 'symbol': 'a', 'timestamp': '36'},
#     {'source': 'okex', 'symbol': 'a', 'timestamp': '37'},
# ]
# data.insert(values)


class LoadDataKline:
    def __init__(self, exchange: Exchange, *args, **kwargs):
        self.exchange = exchange
        super(LoadDataKline, self).__init__(*args, **kwargs)

    def load_all(self):
        logging.info('Loading', self.exchange.id, 'markets...')
        self.exchange.load_markets()
        for sym in self.exchange.symbols:
            print(sym)
        logging.info('Loaded', self.exchange.id, 'markets.')

    def load(self, symbol, timeframe='1m', max_retries=3):

        limit = 100
        earliest_timestamp = self.exchange.milliseconds()
        timeframe_duration_in_seconds = self.exchange.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        ohlcv_dictionary = {}
        ohlcv_list = []
        i = 0
        done = False
        while True:
            logging.info('===========================================================')
            logging.info('Iteration', i)
            fetch_since = earliest_timestamp - timedelta
            logging.info('Fetching', self.exchange.id, symbol, timeframe, 'candles from',
                         self.exchange.iso8601(fetch_since), 'to',
                         self.exchange.iso8601(earliest_timestamp))
            num_retries = 0
            try:
                num_retries += 1
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, fetch_since, limit)
                if len(ohlcv):
                    earliest_timestamp = ohlcv[0][0] - timeframe_duration_in_ms
                    print('Fetched', len(ohlcv), self.exchange.id, symbol, timeframe, 'candles from',
                          self.exchange.iso8601(ohlcv[0][0]), 'to', self.exchange.iso8601(ohlcv[-1][0]))
                else:
                    print('Fetched', len(ohlcv), self.exchange.id, symbol, timeframe, 'candles')
                    done = True
            except Exception as e:
                logging.error(e)
                if num_retries > max_retries:
                    raise
                else:
                    continue
            i += 1
            ohlcv_dictionary = self.exchange.extend(ohlcv_dictionary, self.exchange.indexBy(ohlcv, 0))
            ohlcv_list = self.exchange.sort_by(ohlcv_dictionary.values(), 0)
            if len(ohlcv_list):
                print(ohlcv_list)
                print('Stored', len(ohlcv_list), self.exchange.id, symbol, timeframe, 'candles from',
                      self.exchange.iso8601(ohlcv_list[0][0]), 'to', self.exchange.iso8601(ohlcv_list[-1][0]))
            if done:
                break
        return ohlcv_list


exchan = LoadDataKline(ccxt.okex())

symbol = 'BTC/USDT'

ohlcvs = exchan.load(symbol)
print('Done.')
