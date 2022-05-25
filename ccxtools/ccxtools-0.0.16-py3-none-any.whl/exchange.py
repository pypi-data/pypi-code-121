from abc import ABCMeta, abstractmethod


class Exchange(metaclass=ABCMeta):

    def __init__(self, market):
        self.market = market

    @abstractmethod
    def get_balance(self, ticker):
        raise NotImplementedError


class CcxtExchange(Exchange):

    def __init__(self, market):
        super().__init__(market)
        self.ccxt_inst = None

    def get_balance(self, ticker):
        return self.ccxt_inst.fetch_balance()[ticker]['total']
