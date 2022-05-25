import ccxt
from ccxtools.exchange import CcxtExchange


class Binance(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)

        if market == 'USDT':
            self.ccxt_inst = ccxt.binance({
                'apiKey': config(f'BINANCE_API_KEY{who}'),
                'secret': config(f'BINANCE_SECRET_KEY{who}'),
                'options': {'defaultType': 'future'}
            })
