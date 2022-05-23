from decimal import Decimal
import ccxt
from ccxtools.exchange import CcxtExchange


class Bybit(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)
        self.ccxt_inst = ccxt.bybit({
            'apiKey': config(f'BYBIT_API_KEY{who}'),
            'secret': config(f'BYBIT_SECRET_KEY{who}')
        })

    def get_max_trading_qtys(self):
        markets = self.ccxt_inst.fetch_markets()

        result = {}
        for market in markets:
            if not market['linear']:
                continue

            ticker = market['base']
            result[ticker] = Decimal(market['info']['lot_size_filter']['max_trading_qty'])

        return result

    def get_risk_limit(self, ticker):
        if self.market == 'USDT':
            return self.ccxt_inst.public_linear_get_risk_limit({
                'symbol': f'{ticker}USDT'
            })

    def set_risk_limit(self, ticker, side, risk_id):
        if self.market == 'USDT':
            try:
                return self.ccxt_inst.private_linear_post_position_set_risk({
                    'symbol': f'{ticker}USDT',
                    'side': side,
                    'risk_id': risk_id
                })
            except ccxt.errors.ExchangeError as exchange_error:
                if 'risk id not modified' in str(exchange_error):
                    return {
                        'ret_msg': 'OK',
                        'result': {
                            'risk_id': risk_id
                        }
                    }

                raise Exception(exchange_error)
