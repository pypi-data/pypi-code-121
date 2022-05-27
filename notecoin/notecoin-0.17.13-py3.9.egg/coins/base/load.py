import json
import logging

import ccxt
import pandas as pd
from ccxt.base.exchange import Exchange
from notecoin.base.database import KlineData
from tqdm import tqdm


class LoadDataKline:
    def __init__(self, exchange: Exchange, *args, **kwargs):
        self.table = KlineData()
        self.exchange = exchange
        super(LoadDataKline, self).__init__(*args, **kwargs)

    def load_all(self):
        logging.info('Loading', self.exchange.id, 'markets...')
        self.exchange.load_markets()
        for sym in self.exchange.symbols:
            if ':' not in sym:
                print(sym)
        logging.info('Loaded', self.exchange.id, 'markets.')

    def load(self, symbol, timeframe='1m', max_retries=3):
        limit = 100
        earliest_timestamp = self.exchange.milliseconds()
        timeframe_duration_in_seconds = self.exchange.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        result_dictionary = {}

        pbar = tqdm(range(1000), desc=symbol)
        for _ in pbar:
            fetch_since = earliest_timestamp - timedelta
            result = self.exchange.fetch_ohlcv(symbol, timeframe, fetch_since, limit)
            pbar.set_postfix({'fetch_since': self.exchange.iso8601(result[0][0])})

            if len(result) == 0:
                continue

            result_dictionary = self.exchange.extend(result_dictionary, self.exchange.indexBy(result, 0))
            result_list = self.exchange.sort_by(result_dictionary.values(), 0)

            if len(result_list) == 0:
                continue

            df = pd.DataFrame(result_list, columns=['timestamp', 'open', 'close', 'low', 'high', 'vol'])
            df['symbol'] = 'btc'
            self.table.insert(json.loads(df.to_json(orient='records')))
            earliest_timestamp = result[0][0] - timeframe_duration_in_ms


exchan = LoadDataKline(ccxt.okex())
# exchan.load('BTC/USDT')
exchan.load_all()
