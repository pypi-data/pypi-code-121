import ccxt
from ccxtools.exchange import CcxtExchange


class Okx(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)
        self.ccxt_inst = ccxt.okex({
            'apiKey': config(f'OKX_API_KEY{who}'),
            'secret': config(f'OKX_SECRET_KEY{who}'),
            'password': config(f'OKX_PASSWORD{who}'),
        })

    def set_leverage(self, ticker, leverage):
        if self.market == 'USDT':
            return self.ccxt_inst.set_leverage(leverage, f'{ticker}-USDT-SWAP', {'mgnMode': 'cross'})
