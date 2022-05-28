from ktrader.candle_trader.component.record import Record
from ktrader.utils.price import round_px
from ktrader import utils
from copy import deepcopy
import warnings


class Order():
    def __init__(self, record):
        self.__record: Record = record

    @staticmethod
    def get_empty_orderData():
        '''
        init需要更新的参数：
            orderType       订单类型 str
            posSide         方向 long做多，short做空
            buyIndex        购买时候的index int
            orderDatetime   订单开始的时间，%Y-m-%d %H:%M:%S str
            buyLine         购买的价格 float
            tpLine          止盈的价格 float
            slLine          止损的价格 float
            volCcy24        24小时的USDT成交量 float
            buyMoney        买入的金额 float
        close需要更新的参数：
            endType         订单终止的方式
            sellIndex       卖出时候的index int
            endDatetime     订单终止的时间，%Y-%m-%d %H:%M:%S str
            sellLine        卖出的价格 float
            holdMinute      从订单开始到订单结束的时间，单位分钟 int
            sellMoney       卖出的金额（包含抛出） float
            diff            利润率 float
            profit          利润 float
        process需要更新的参数：
            processMax     订单开始到订单终止的最大价格
            processMaxV    订单开始到订单终止的最大涨幅 float
            processMin     订单开始到订单终止的最小价格
            processMinV    订单开始到订单终止的最大跌幅 float
        '''
        orderData = {
            # 订单类型 str
            'orderType': None,
            # 方向：long做多，short做空
            'posSide': None,
            # 购买时候的index int
            'buyIndex': None,
            # 订单开始的时间，%Y-m-%d %H:%M:%S, str
            'orderDatetime': None,
            # 购买的价格 float
            'buyLine': None,
            # 止盈的价格 float
            'tpLine': None,
            # 止损的价格 float
            'slLine': None,
            # 24小时的USDT成交量 float
            'volCcy24': None,
            # 买入的金额 float
            'buyMoney': None,
            # 订单终止的方式 str
            'endType': None,
            # 卖出时候的index int
            'sellIndex': None,
            # 订单终止的时间，%Y-%m-%d %H:%M:%S str
            'endDatetime': None,  # str
            # 卖出的价格 float
            'sellLine': None,
            # 从订单开始到订单结束的时间，单位分钟 int
            'holdMinute': None,
            # 卖出的金额（包含抛出） float
            'sellMoney': None,
            # 利润率 float
            'diff': None,
            # 手续费
            'commission': None,
            # 利润 float
            'profit': None,
            #  订单开始到订单终止的最大价格
            'processMax': None,
            #  订单开始到订单终止的最大涨幅 float
            'processMaxV': None,
            #  订单开始到订单终止的最小价格
            'processMin': None,
            # 订单开始到订单终止的最大跌幅 float
            'processMinV': None,
        }
        return deepcopy(orderData)

    def to_historyOrderDatas(self, orderDatas):
        if orderDatas:
            for orderData in orderDatas:
                try:
                    self.__record.currentOrderDatas.remove(orderData)
                    self.__record.historyOrderDatas.append(orderData)
                    self.__record.money += orderData['sellMoney']
                    # if orderData['posSide'] == 'long':
                    #     self.__record.last_sellLine['buy'] = orderData['sellLine']
                    # elif orderData['posSide'] == 'short':
                    #     self.__record.last_sellLine['sell'] = orderData['sellLine']
                except:
                    pass

    def to_currentOrderDatas(self, orderDatas):
        if orderDatas:
            for orderData in orderDatas:
                self.__record.currentOrderDatas.append(orderData)
                self.__record.money -= orderData['buyMoney']

    def start_orderData(self, posSide, buyLine, buyMoney, orderType=None, tpRate=None, slRate=None, firm=True,
                        **kwargs):
        orderData = self.get_empty_orderData()
        buyLine = round_px(buyLine)
        # 验证是否能以buyLine进行购买
        if buyLine >= self.__record.low and buyLine <= self.__record.high:
            orderData['buyLine'] = buyLine
        # 如果不能成功购买
        else:
            # firm等于True、则会收盘的时候购买
            if firm == True:
                buyLine = self.__record.close
                orderData['buyLine'] = buyLine
                # todo 报告警告
            # 报告异常 todo + ts
            else:
                raise Exception(
                    'buyLine:{buyLine} not between low:{low}~high{high}'.format(
                        buyLine=buyLine,
                        low=self.__record.low,
                        high=self.__record.high,
                    )
                )
        orderData['orderType'] = orderType
        orderData['orderDatetime'] = utils.date.ts_to_datetime(self.__record.candle[self.__record.index, 0])
        orderData['orderTs'] = self.__record.candle[self.__record.index, 0]
        orderData['buyIndex'] = self.__record.index
        if posSide == 'long':
            if tpRate:
                tpLine = buyLine * (1 + abs(tpRate))
                slLine = buyLine * (1 - abs(slRate))
            else:
                tpLine = (abs(self.__record.rule.SIDE_BUY_TP) + 1) * buyLine
                slLine = (-abs(self.__record.rule.SIDE_BUY_SL) + 1) * buyLine
        elif posSide == 'short':
            if tpRate:
                tpLine = buyLine * (1 - abs(tpRate))
                slLine = buyLine * (1 + abs(slRate))
            else:
                tpLine = (-abs(self.__record.rule.SIDE_SELL_TP) + 1) * buyLine
                slLine = (abs(self.__record.rule.SIDE_SELL_SL) + 1) * buyLine
        else:
            raise Exception('error posSide')  # todo
        orderData['tpLine'] = round_px(tpLine)
        orderData['slLine'] = round_px(slLine)
        orderData['buyMoney'] = buyMoney
        orderData['posSide'] = posSide
        orderData['processMax'] = buyLine
        orderData['processMin'] = buyLine
        orderData['processMaxV'] = 0
        orderData['processMinV'] = 0
        if kwargs:
            for key in kwargs:
                orderData[key] = kwargs[key]
        return orderData

    def close_orderData(self, orderData, sellLine, endType=None, index=None, firm=True, **kwargs):
        if not index:
            index = self.__record.index
        sellLine = orderData['sellLine'] = round_px(sellLine)
        # 如果卖出价格不在low~high之间
        if not (sellLine >= self.__record.low and sellLine <= self.__record.high):
            if firm == True:
                sellLine = self.__record.close
                orderData['sellLine'] = sellLine
                # todo + warning
            else:
                # todo + ts
                raise Exception(
                    'sellLine:{sellLine} not between low:{low}~high{high}'.format(
                        sellLine=sellLine,
                        low=self.__record.low,
                        high=self.__record.high,
                    )
                )

        orderData['sellIndex'] = self.__record.index
        orderData['endType'] = endType
        orderData['endDatetime'] = utils.date.ts_to_datetime(self.__record.candle[index, 0])
        orderData['endTs'] = self.__record.candle[self.__record.index, 0]
        orderData['sellLine'] = sellLine
        orderData['holdMinute'] = utils.date.derta_datetime_minute(
            orderData['orderDatetime'], orderData['endDatetime']
        )

        s = orderData['sellLine']
        b = orderData['buyLine']
        r = self.__record.rule.COMMISSION_RATE
        l = self.__record.rule.LEVEL
        if orderData['posSide'] == 'long':
            orderData['commission'] = (l * r + (1 - l * r) * (l * (s - b) + b) / b * l * r) * orderData['buyMoney']
            orderData['diff'] = round((1 - l * r) ** 2 * (l * (s - b) + b) / b - 1, 5)

        elif orderData['posSide'] == 'short':
            orderData['commission'] = l * r + (1 - l * r) * (b + (b - s) * l) / b * l * r * orderData['buyMoney']
            orderData['diff'] = round((1 - l * r) ** 2 * (b + (b - s) * l) / b - 1, 5)
        else:
            raise Exception(orderData['posSide'])
        orderData['sellMoney'] = round(orderData['buyMoney'] * (1 + orderData['diff']), 5)
        orderData['profit'] = round(orderData['diff'] * orderData['buyMoney'], 5)
        # orderData['open'] = self.__record.open
        # orderData['close'] = self.__record.close
        # orderData['high'] = self.__record.high
        # orderData['low'] = self.__record.low

        # 更新过程中的最高与最低价格
        # orderData['processMax'] = max(
        #     self.__record.candle[orderData['buyIndex']:orderData['sellIndex'], 2]
        # )
        # orderData['processMin'] = min(
        #     self.__record.candle[orderData['buyIndex']:orderData['sellIndex'], 3]
        # )
        # orderData['processMaxV'] = round((orderData['processMax'] - orderData['buyLine']) / orderData['buyLine'], 4)
        # orderData['processMinV'] = round((orderData['processMin'] - orderData['buyLine']) / orderData['buyLine'], 4)
        if kwargs:
            for key in kwargs:
                orderData[key] = kwargs[key]
        return orderData
