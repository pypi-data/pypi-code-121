from ktrader.candle_trader.component import period, order, rule, trade, record, analysis
from ktrader import utils

# from importlib import reload
# reload(period)
# reload(order)
# reload(rule)
# reload(trade)
# reload(utils)
# reload(record)
# reload(analysis)



class CandlerTrader():
    def __init__(self, candle, rule):
        self.rule = rule
        self.record = record.Record(candle=candle, rule=rule, index=0)
        self.period = period.Period(record=self.record)
        self.order = order.Order(self.record)
        self.trade = trade.Trade(record=self.record, period=self.period, order=self.order)
        self.analysis = analysis.Analysis(record=self.record, order=self.order)
        self.setup()

    def setup(self):
        # to override
        pass

    def buy(self, *args, **kwargs):
        # to override
        pass

    def sell(self, *args, **kwargs):
        # to override
        pass

    def run(self, start_date=None, end_date=None, clear=True):
        start_index = utils.candle.get_index_by_date(
            candle=self.record.candle,
            date=start_date,
            default=0
        )
        end_index = utils.candle.get_index_by_date(
            candle=self.record.candle,
            date=end_date,
            default=self.record.candle.shape[0]
        )

        for index in range(start_index, end_index - 1):
            self.index = self.record.index = index
            self.record.update()

            self.order.to_historyOrderDatas(self.trade.periodThrow())
            tpSellOrders = [order for order in self.trade.tpSell()]
            self.order.to_historyOrderDatas(tpSellOrders)

            slThrowOrders = [order for order in self.trade.slThrow()]
            self.order.to_historyOrderDatas(slThrowOrders)
            if self.period.isPeriodSell() and not slThrowOrders:
                self.order.to_historyOrderDatas(self.sell())
            if self.period.isPeriodBuy() and not tpSellOrders and not slThrowOrders:
                self.order.to_currentOrderDatas(self.buy())

        if clear:
            self.order.to_historyOrderDatas(self.trade.marketThrow(self.record.currentOrderDatas))

    # 调用
    def start_orderData(self, posSide, buyLine, buyMoney, orderType=None, tpRate=None, slRate=None, firm=True,
                        **kwargs):
        return self.order.start_orderData(posSide=posSide, buyLine=buyLine, buyMoney=buyMoney, orderType=orderType,
                                          tpRate=tpRate, slRate=slRate, firm=firm, **kwargs)

    def close_orderData(self, orderData, sellLine, endType=None, index=None, firm=True, **kwargs):
        return self.order.close_orderData(orderData=orderData, sellLine=sellLine, endType=endType, index=index,
                                          firm=firm, **kwargs)

    # attribute ---------------------------------
    @property
    def open(self):
        return self.record.open

    @property
    def high(self):
        return self.record.high

    @property
    def low(self):
        return self.record.low

    @property
    def close(self):
        return self.record.close

    @property
    def day_index(self):
        if hasattr(self.record, 'day_index'):
            return self.record.day_index
        else:
            return None

    @property
    def day_open(self):
        return self.record.day_open

    @property
    def day_high(self):
        return self.record.day_high

    @property
    def day_low(self):
        return self.record.day_low

    '''
    todo 当前时间，当前分钟
    '''
