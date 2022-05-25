import ccxt
from ccxtools.exchange import CcxtExchange


class Huobi(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)

        if market == 'USDT':
            self.ccxt_inst = ccxt.huobi({
                'apiKey': config(f'HUOBI_API_KEY{who}'),
                'secret': config(f'HUOBI_SECRET_KEY{who}'),
                'options': {
                    'defaultType': 'swap',
                    'defaultSubType': 'linear'
                }
            })

    def get_balance(self, ticker):
        response = self.ccxt_inst.contractPrivatePostLinearSwapApiV1SwapCrossAccountPositionInfo(params={'margin_account': 'USDT'})
        return float(response['data']['margin_balance'])
