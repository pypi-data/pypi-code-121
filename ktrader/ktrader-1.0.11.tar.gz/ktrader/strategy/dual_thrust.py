from ktrader import candle_trader
from ktrader.candle_trader.component import rule
import numpy as np
import matplotlib.pyplot as plt
import datetime


# import importlib
# importlib.reload(candle_trader)


def isNone(obj):
    return type(obj).__name__ == 'NoneType'


def get_dualThrust_array(candle, n: int, ks: float, kx: float):
    '''
    :param: candle
    :param: 前n分钟
    '''
    dualThrust_list = []
    for i in range(n, candle.shape[0], n):
        # 前bar的数据
        last_k_array = candle[i - n:i]
        hh = last_k_array[:, 2].max()  # 最高价的最高价
        hc = last_k_array[:, 4].max()  # 最高价的收盘价
        lc = last_k_array[:, 4].min()  # 最低价的收盘价
        ll = last_k_array[:, 3].min()  # 最低价的最低价
        range_ = max(hh - lc, hc - ll)
        open = candle[i, 1]  # 开盘价
        range_ks = open + ks * range_
        range_kx = open - kx * range_
        # 还剩下的数据长度
        length = min(n, candle.shape[0] - i)
        for ts in candle[i:i + length, 0]:
            dualThrust_list.append([ts, range_ks, range_kx, hh, hc, lc, ll])
    return np.array(dualThrust_list)


class Rule(rule.Rule):
    LEVEL = 1
    SIDE_BUY_TP = 9999
    SIDE_BUY_SL = 1

    SIDE_SELL_TP = 9999
    SIDE_SELL_SL = 1


class DualThrust(candle_trader.CandlerTrader):
    def __init__(self, candle, n, ks, kx, position=2, money=1, reverse=False, rule=Rule()):
        self.reverse = reverse
        self.position = position
        self.money = money
        self.n = n
        self.ks = ks
        self.kx = kx
        self.dualThrust_array = get_dualThrust_array(
            candle=candle,
            n=self.n,
            ks=self.ks,
            kx=self.kx,
        )
        candle = candle[n:]  # 去掉前n行的candle
        super(DualThrust, self).__init__(candle=candle, rule=rule)

    @property
    def range_ks(self):
        return self.dualThrust_array[self.index, 1]

    @property
    def range_kx(self):
        return self.dualThrust_array[self.index, 2]

    def buy_wapper(self):
        if self.reverse == False:
            # 做多
            if not hasattr(self, 'latest_buy_range_ks') or self.range_ks != self.latest_buy_range_ks:
                if self.high >= self.range_ks:
                    yield self.start_orderData(
                        orderType='dualThrust',
                        posSide='long',
                        buyLine=self.range_ks,
                        buyMoney=self.money,
                        # tpRate=1,
                        # slRate=1,
                    )
                    self.latest_buy_range_ks = self.range_ks
            # 做空
            if not hasattr(self, 'latest_buy_range_kx') or self.range_kx != self.latest_buy_range_kx:
                if self.low <= self.range_kx:
                    yield self.start_orderData(
                        orderType='dualThrust',
                        posSide='short',
                        buyLine=self.range_kx,
                        buyMoney=self.money,
                        # tpRate=1,
                        # slRate=1,
                    )
                    self.latest_buy_range_kx = self.range_kx
        elif self.reverse:
            # 做空
            if not hasattr(self, 'latest_buy_range_ks') or self.range_ks != self.latest_buy_range_ks:
                if self.high >= self.range_ks:
                    yield self.start_orderData(
                        orderType='dualThrust',
                        posSide='short',
                        buyLine=self.range_ks,
                        buyMoney=self.money,
                        # tpRate=1,
                        # slRate=1,
                    )
                    self.latest_buy_range_ks = self.range_ks
            # 做空
            if not hasattr(self, 'latest_buy_range_kx') or self.range_kx != self.latest_buy_range_kx:
                if self.low <= self.range_kx:
                    yield self.start_orderData(
                        orderType='dualThrust',
                        posSide='long',
                        buyLine=self.range_kx,
                        buyMoney=self.money,
                        # tpRate=1,
                        # slRate=1,
                    )
                    self.latest_buy_range_kx = self.range_kx

    def buy(self):
        orderDatas = [orderData for orderData in self.buy_wapper()]
        for i in range(self.position - len(self.record.currentOrderDatas)):
            if i < len(orderDatas):
                yield orderDatas[i]

    def sell(self):
        if self.reverse == False:
            for orderData in self.record.currentOrderDatas:
                # 多单
                if orderData['posSide'] == 'long' and self.low <= self.range_kx:
                    ts = self.record.candle[self.index, 0]
                    yield self.close_orderData(
                        orderData=orderData,
                        sellLine=self.range_kx,
                    )
                # 空单
                elif orderData['posSide'] == 'short' and self.high >= self.range_ks:
                    yield self.close_orderData(
                        orderData=orderData,
                        sellLine=self.range_ks,
                    )
        else:
            for orderData in self.record.currentOrderDatas:
                # 多单
                if orderData['posSide'] == 'long' and self.high >= self.range_ks:
                    ts = self.record.candle[self.index, 0]
                    yield self.close_orderData(
                        orderData=orderData,
                        sellLine=self.range_kx,
                    )
                # 空单
                elif orderData['posSide'] == 'short' and self.low <= self.range_kx:
                    yield self.close_orderData(
                        orderData=orderData,
                        sellLine=self.range_ks,
                    )

    def plot(self, open=1, range_ks=1, range_kx=1, point=1, figsize=(20, 8)):
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
        plt.rcParams['font.size'] = 15
        plt.figure(figsize=figsize)
        legends = []
        linewidth = max(figsize[0] / 20 * 1, 1)
        pointsize = max(figsize[0] / 20 * 100, 100)
        ticksfontsize = 10 * figsize[0] / 20
        labelfontsize = 15 * figsize[0] / 20
        titlefontsize = 15 * figsize[0] / 20

        ts = self.record.candle[:, 0]
        if open:
            open_line = self.record.candle[:, 1]
            plt.plot(ts, open_line, linewidth=linewidth)
            legends.append('开盘价格')
        if range_ks:
            ks_line = self.dualThrust_array[:, 1]
            plt.plot(ts, ks_line, linewidth=linewidth)
            legends.append('上轨range_ks')
        if range_kx:
            kx_line = self.dualThrust_array[:, 2]
            plt.plot(ts, kx_line, linewidth=linewidth)
            legends.append('下轨range_kx')
        if point:
            long_buy_points = []
            long_sell_points = []
            short_buy_points = []
            short_sell_points = []
            for historyOrderData in self.record.historyOrderDatas:
                posSide = historyOrderData['posSide']
                buyIndex = historyOrderData['buyIndex']
                sellIndex = historyOrderData['sellIndex']
                buyLine = historyOrderData['buyLine']
                sellLine = historyOrderData['sellLine']
                buyTs = self.record.candle[buyIndex, 0]
                sellTs = self.record.candle[sellIndex, 0]
                if posSide == 'long':
                    long_buy_points.append([buyTs, buyLine])
                    long_sell_points.append([sellTs, sellLine])
                elif posSide == 'short':
                    short_buy_points.append([buyTs, buyLine])
                    short_sell_points.append([sellTs, sellLine])

            long_buy_points = np.array(long_buy_points)
            long_sell_points = np.array(long_sell_points)

            short_buy_points = np.array(short_buy_points)
            short_sell_points = np.array(short_sell_points)

            if not isNone(long_buy_points):
                buy_points_ts = long_buy_points[:, 0]
                buy_points_price = long_buy_points[:, 1]
                plt.scatter(buy_points_ts, buy_points_price * 1.001, color='r', s=pointsize, marker='^')
                legends.append('买入开多')

            if not isNone((long_sell_points)):
                sell_points_ts = long_sell_points[:, 0]
                sell_points_price = long_sell_points[:, 1]
                plt.scatter(sell_points_ts, sell_points_price * 0.999, color='k', s=pointsize, marker='^')
                legends.append('卖出平多')

            if not isNone(short_buy_points):
                buy_points_ts = short_buy_points[:, 0]
                buy_points_price = short_buy_points[:, 1]
                plt.scatter(buy_points_ts, buy_points_price * 1.001, color='r', s=pointsize, marker='v')
                legends.append('卖出开空')

            if not isNone((short_sell_points)):
                sell_points_ts = short_sell_points[:, 0]
                sell_points_price = short_sell_points[:, 1]
                plt.scatter(sell_points_ts, sell_points_price * 0.999, color='k', s=pointsize, marker='v')
                legends.append('买入平空')
        xticks = []
        xlabels = []
        ts_min = self.record.candle[:, 0].min()
        ts_max = self.record.candle[:, 0].max()
        start_date = datetime.datetime.fromtimestamp(int(ts_min / 1000))
        end_date = datetime.datetime.fromtimestamp(int(ts_max / 1000))
        derta_day = (end_date - start_date).days
        for day in range(derta_day + 3):
            date_str = (start_date + datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            date_ts = datetime.datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000
            xticks.append(date_ts)
            xlabels.append(date_str)
        plt.xticks(ticks=xticks, labels=xlabels, rotation=90, fontsize=10 * figsize[0] / 20)
        plt.xlabel('日期', fontsize=labelfontsize)
        plt.ylabel('价格', fontsize=labelfontsize)
        plt.title('交易过程历史K线图', fontsize=titlefontsize)
        plt.grid(linewidth=linewidth * 0.5)
        plt.legend(legends)

        plt.show()


if __name__ == '__main__':
    from kqt_tool.load import load_array_map_by_date
    from importlib import reload

    candle_map = load_array_map_by_date(start_date='2022-01-01', end_date='2022-01-10', instIds=['BTC-USDT'])
    BTC = candle_map['BTC-USDT']

    from ktrader.candle_trader.component import rule

    reload(rule)

    R = rule.Rule()

    dt = DualThrust(candle=BTC, rule=R, n=60 * 12, ks=0.3, kx=0.3, position=1, reverse=True)

    dt.run()
    # for order in dt.record.historyOrderDatas:
    #     print(order)
    dt.plot()
    dt.analysis.plot_profit(by='day')
    print(dt.analysis.df_profit(by='day'))
