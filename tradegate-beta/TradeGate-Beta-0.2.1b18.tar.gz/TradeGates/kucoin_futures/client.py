from kucoin_futures.marke_data.market_data import MarketData
from kucoin_futures.trade.trade import TradeData
from kucoin_futures.user.user import UserData
from kucoin_futures.ws_token.token import GetToken


class FuturesMarket(MarketData):
    pass


class FuturesUser(UserData):
    pass


class FuturesTrade(TradeData):
    pass


class FuturesWsToken(GetToken):
    pass
