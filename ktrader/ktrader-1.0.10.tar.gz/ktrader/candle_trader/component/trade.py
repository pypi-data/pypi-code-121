from ktrader.candle_trader.component.record import Record
from ktrader.candle_trader.component.period import Period
from ktrader.candle_trader.component.order import Order


class Trade():
    def __init__(self, record, period, order):
        self.__record: Record = record
        self.__period: Period = period
        self.__orderData: Order = order

    # 止盈卖出
    def tpSell(self):
        index = self.__record.index
        for orderData in self.__record.currentOrderDatas:
            posSide = orderData['posSide']
            # 做多与做多
            if (posSide == 'long' and self.__record.high >= orderData['tpLine']) or \
                    (posSide == 'short' and self.__record.low <= orderData['tpLine']):
                sellOrderData = self.__orderData.close_orderData(
                    orderData=orderData, endType='tp', sellLine=orderData['tpLine'], index=index
                )
                yield sellOrderData

    # 止损抛出
    def slThrow(self):
        # index = self.__record.index
        # for orderData in self.__record.currentOrderDatas:
        #     side = orderData['side']
        # # 做多与做多
        #     if (side == 'buy' and self.__record.low <= orderData['slLine']) or \
        #             (side == 'sell' and self.__record.high >= orderData['slLine']):
        #         throwOrderData = self.__orderData.close_orderData(
        #             orderData=orderData, endType='sl', sellLine=orderData['slLine'], index=index
        #         )
        #         yield throwOrderData
        index = self.__record.index
        for orderData in self.__record.currentOrderDatas:
            posSide = orderData['posSide']
            # 做多与做多
            if (posSide == 'long' and self.__record.open <= orderData['slLine']) or \
                    (posSide == 'short' and self.__record.open >= orderData['slLine']):
                throwOrderData = self.__orderData.close_orderData(
                    orderData=orderData, endType='sl', sellLine=self.__record.close, index=index
                )
                yield throwOrderData

    # 按照时间段抛出全部
    def periodThrow(self):
        index = self.__record.index
        if self.__period.isPeriodThrow():
            for orderData in self.__record.currentOrderDatas:
                periodThrowOrderData = self.__orderData.close_orderData(
                    orderData, endType='pt', sellLine=self.__record.open, index=index,
                )
                yield periodThrowOrderData

    def marketThrow(self, orderDatas):
        for orderData in orderDatas:
            marketThrowOrderData = self.__orderData.close_orderData(
                orderData, endType='mt', sellLine=self.__record.open
            )
            yield marketThrowOrderData

    def buy(self, *args, **kwargs):
        pass

    def sell(self, *args, **kwargs):
        pass
