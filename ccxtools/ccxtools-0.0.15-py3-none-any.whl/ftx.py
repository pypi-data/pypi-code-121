import ccxt
from ccxtools.exchange import CcxtExchange


class Ftx(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)

        self.ccxt_inst = ccxt.ftx({
            'apiKey': config(f'FTX_API_KEY{who}'),
            'secret': config(f'FTX_SECRET_KEY{who}')
        })
