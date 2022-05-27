import math
import pandas as pd
import time
from datetime import datetime, timedelta
from ..generic.spot_fetching import *
from ..util.logger import ProcedureRecorder
from cy_data_access.models.position import *
from cy_widgets.trader.exchange_trader import *
from cy_widgets.logger.trading import *
from cy_widgets.strategy.exchange.aims import *
from cy_widgets.exchange.provider import ExchangeType


class BinanceAIMS:
    """AIMS Procedure
    Require: 连接 DB_POSITION 数据库
    """

    def __init__(self,
                 coin_pair: CoinPair,
                 time_frame,
                 provider: CCXTProvider,
                 signal_scale,
                 ma_periods,
                 sell_threshold,
                 invest_base_amount,
                 recorder: ProcedureRecorder,
                 fee_percent=0,  # 订单里已经扣了，这里不用手动算
                 debug=False):
        self.__df = pd.DataFrame()
        self.__provider = provider
        self.__recorder = recorder
        self.__coin_pair = coin_pair
        self.__recorder.append_summary_log(
            '**{} - {} - AIMS**'.format(provider.display_name.upper(), coin_pair.formatted().upper()))
        self.__recorder.append_summary_log(
            '**日期**: {} \n'.format(DateFormatter.convert_local_date_to_string(datetime.now(), "%Y-%m-%d")))
        self.__fee_percent = fee_percent
        # 直接从远往近抓
        self.__configuration = ExchangeFetchingConfiguration(
            coin_pair, time_frame, 3, ExchangeFetchingType.FILL_RECENTLY, debug=debug)
        # 策略参数
        self.__ma_periods = ma_periods
        self.__signal_scale = signal_scale
        self.__sell_threshold = sell_threshold
        # 交易
        self.__invest_base_amount = invest_base_amount

    def run_task(self, retry_time=3):
        try:
            while True:
                self.fetch_candle()
                # 循环，直到最后一条数据是今天的
                if self.__df.shape[0] > 0 and self.__df.iloc[-1][COL_CANDLE_BEGIN_TIME].dayofweek == datetime.utcnow().weekday():
                    break
                self.__recorder.record_exception("未抓取到今天的 K 线，稍后重试")
                time.sleep(3)
            invest_ratio = self.calculate_signal()
            if not self.__configuration.debug:
                # debug 不下单
                self.handle_signal(invest_ratio)
            else:
                print(invest_ratio)
        except Exception as e:
            self.__recorder.append_summary_log(str(e))
            if retry_time > 0:
                self.__recorder.append_summary_log('获取 K 线失败，3 秒后重试')
                time.sleep(3)
                self.run_task(retry_time=retry_time - 1)
            else:
                self.__recorder.record_summary_log('获取 K 线失败，不重试了，跳过')

    def fetch_candle(self):
        """ 获取 K 线 """
        def __get_latest_date():
            if self.__df.shape[0] > 0:
                return self.__df[COL_CANDLE_BEGIN_TIME].iloc[-1]
            return datetime.now() - timedelta(days=self.__ma_periods + 15)  # 往前多加15天开始

        def __save_df(data_df: pd.DataFrame):
            before_count = self.__df.shape[0]

            # 为了去重
            data_df.set_index(COL_CANDLE_BEGIN_TIME, inplace=True)
            if before_count > 0:
                self.__df.set_index(COL_CANDLE_BEGIN_TIME, inplace=True)
            df_res = pd.concat([self.__df, data_df[~data_df.index.isin(self.__df.index)]])
            df_res.update(data_df)

            self.__df = df_res
            # 排序后重置 index
            self.__df.sort_index(inplace=True)
            self.__df.reset_index(inplace=True)

            after_count = self.__df.shape[0]
            # 前后数量不一致，说明有新数据，继续尝试获取
            return before_count != after_count

        procedure = ExchangeFetchingProcedure(ExchangeFetcher(self.__provider),
                                              self.__configuration,
                                              None,
                                              __get_latest_date,
                                              __save_df)

        # Fill to Latest
        procedure.run_task()

        if self.__configuration.debug:
            print(self.__df)

        self.__recorder.record_procedure("获取 K 线成功")

    @property
    def __position(self):
        return AIMSPosition.position_with(self.__provider.display_name, self.__coin_pair.formatted())

    @property
    def __trader_logger(self):
        return TraderLogger(self.__provider.display_name, self.__coin_pair.formatted(), 'Spot', self.__recorder)

    def calculate_signal(self):
        # Signal Calculation
        strategy = AutoInvestVarietalStrategy(signal_scale=self.__signal_scale,
                                              ma_periods=self.__ma_periods)
        signals = strategy.calculate_signals(self.__df, False)
        # Debug 下打印一点信号看看
        if self.__configuration.debug:
            print(signals[-200:])
        return signals.iloc[-1][COL_SIGNAL]

    def handle_signal(self, signal):
        """处理信号"""
        if signal > 0:
            self.__recorder.append_summary_log('**信号**: 买入({}) \n'.format(signal))
            # 买入
            self.handle_buying(signal * self.__invest_base_amount)
        else:
            position = self.__position
            open_price = self.__df.iloc[-1][COL_CLOSE]
            # P/L
            pol = open_price / (position.cost / position.hold) if position.hold > 0 else 0
            if pol > self.__sell_threshold:
                # 用数据库判断卖出，这里再取实际的仓位数
                amount = self.__provider.ccxt_object_for_order.fetch_balance()['free'][self.__coin_pair.trade_coin]
                # 卖出
                self.handle_selling(amount)
            else:
                # 无信号 结束
                self.__recorder.append_summary_log('**信号**: 无 \n')
                if pol > 0:
                    msg = """**持仓数量**: {} {} \n
**仓位成本**: {} {} \n
**仓位均价**: {} \n
**P/L**: {}%
""".format(round(position.hold, 8), self.__coin_pair.trade_coin.upper(),
                        round(position.cost, 8), self.__coin_pair.base_coin.upper(),
                        round((position.cost / position.hold) if position.hold > 0 else 0, 8), round(100*pol, 2))
                    self.__recorder.append_summary_log(msg)
                self.__recorder.record_summary_log()

    def handle_buying(self, amount):
        # 下单数量
        self.__recorder.append_summary_log('**下单数量**: {} {}\n'.format(amount, self.__coin_pair.base_coin.upper()))
        # ers
        order = Order(self.__coin_pair, amount, 0)  # Only set base coin amount
        executor = ExchangeOrderExecutorFactory.executor(self.__provider, order, self.__trader_logger)
        # place order
        response = executor.handle_long_order_request()
        if response is None:
            self.__recorder.record_summary_log('**下单失败**')
            return
        # handle order info
        price = response['average']
        cost = response['cost']
        filled = response['filled']
        # Binance 手续费已经扣掉了
        # {'id': '701037299',
        # 'clientOrderId': 'Se8IFlpHyWpsY7OaYkhKC1',
        # 'timestamp': 1597589153872,
        # 'datetime': '2020-08-16T14:45:53.872Z',
        # 'lastTradeTimestamp': None,
        # 'symbol': 'BNB/USDT',
        # 'type': 'limit',
        # 'side': 'buy',
        # 'price': 23.3236,
        # 'amount': 0.47,
        # 'cost': 10.854319,
        # 'average': 23.094295744680853,
        # 'filled': 0.47,
        # 'remaining': 0.0,
        # 'status': 'closed',
        # 'fee': None,
        # 'trades': None}
        buy_amount = math.floor(filled * (1 - self.__fee_percent) * 1e8) / 1e8  # *1e8 向下取整再 / 1e8
        msg = """**成交价格**: {} \n
**成交总价**: {} {}\n
**成交数量**: {} {}
""".format(round(price, 6), round(cost, 6), self.__coin_pair.base_coin.upper(), round(buy_amount, 8), self.__coin_pair.trade_coin.upper())
        self.__recorder.append_summary_log(msg)
        # 更新 Cost/Hold 到数据库
        position = self.__position
        position.update(cost, buy_amount)
        msg = """**持仓数量**: {} {} \n
**仓位成本**: {} {} \n
**仓位均价**: {}
""".format(round(position.hold, 8), self.__coin_pair.trade_coin.upper(),
           round(position.cost, 8), self.__coin_pair.base_coin.upper(),
           round((position.cost / position.hold) if position.hold > 0 else 0, 8))
        self.__recorder.record_summary_log(msg)

    def handle_selling(self, amount):
        # 下单数量
        self.__recorder.append_summary_log('**信号**: 卖出 \n')
        self.__recorder.append_summary_log('**下单数量**: {} {}\n'.format(amount, self.__coin_pair.trade_coin.upper()))
        # ers
        order = Order(self.__coin_pair, 0, amount, side=OrderSide.SELL)  # Only set trade coin amount
        executor = ExchangeOrderExecutorFactory.executor(self.__provider, order, self.__trader_logger)
        # place order
        response = executor.handle_close_order_request()
        if response is None:
            self.__recorder.record_summary_log('**下单失败**')
            return
        # handle order
        # 'id': '701205190',
        # 'clientOrderId': 'Iep2bjMRJGSUBS0qDq9AhS',
        # 'timestamp': 1597595099771,
        # 'datetime': '2020-08-16T16:24:59.771Z',
        # 'lastTradeTimestamp': None,
        # 'symbol': 'BNB/USDT',
        # 'type': 'limit',
        # 'side': 'sell',
        # 'price': 22.979,
        # 'amount': 0.92,
        # 'cost': 21.355224,
        # 'average': 23.2122,
        # 'filled': 0.92,
        # 'remaining': 0.0,
        # 'status': 'closed',
        # 'fee': None,
        # 'trades': None}
        price = response['average']
        cost = response['cost']
        filled = response['filled']
        position = self.__position
        msg = """**成交价格**: {} \n
**成交总价**: {} {}\n
**成交数量**: {} {}\n
**仓位成本**: {} {}
""".format(round(price, 6), round(cost, 6), self.__coin_pair.base_coin.upper(), round(filled, 8), self.__coin_pair.trade_coin.upper(),
           round(position.cost, 8), self.__coin_pair.base_coin.upper())
        # 更新卖出记录
        close_pos = AIMSPositionSelling.with_aims_position(position)
        close_pos.close_price = price
        close_pos.profit_amount = cost - position.cost
        close_pos.date = datetime.now()
        close_pos.save()
        # 更新 Cost/Hold 到数据库
        position.reset()
        # 通知
        self.__recorder.record_summary_log(msg)
