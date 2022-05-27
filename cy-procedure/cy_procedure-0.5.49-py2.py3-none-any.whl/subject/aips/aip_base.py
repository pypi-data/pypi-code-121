import math
import pandas as pd
from datetime import datetime, timedelta
from ...generic.spot_fetching import *
from ...util.logger import ProcedureRecorder
from cy_widgets.trader.exchange_trader import *
from cy_widgets.logger.trading import *
from cy_widgets.strategy.exchange.autobuy import *
from cy_widgets.exchange.provider import ExchangeType
from cy_data_access.models.position import *


class AIPBase:
    precision_coefficient = 4
    precision_amount = 6
    precision_price = 6

    def __init__(self,
                 coin_pair: CoinPair,
                 time_frame,
                 signal_provider,
                 day_of_week,
                 ma_periods,
                 trader_provider,
                 invest_base_amount,
                 recorder: ProcedureRecorder,
                 debug=False,
                 fee_percent=0):
        """余币宝转出USDT + 定投买入 + 余币宝转入BTC

        Parameters
        ----------
        coin_pair : CoinPair
            币对信息
        time_frame : TimeFrame
            K线间隔
        signal_provider : CCXTProvider
            抓取K线
        interval_days : Int
            计算定投信号用，间隔天数
        ma_periods : Int
            计算定投信号用，MA计算参数
        start_index : Int
            计算定投信号用，相对星期
        trader_provider : CCXTProvider
            交易用
        invest_base_amount : Double
            定投基准额
        recorder : ProcedureRecorder
            记录
        fee_percent : Double
            手续费
        """
        self.__df = pd.DataFrame()
        self.signal_provider = signal_provider
        self.trader_provicer = trader_provider
        self.recorder = recorder
        self.coin_pair = coin_pair
        self.recorder.append_summary_log(F'**{coin_pair.formatted().upper()} - 定投**')
        self.fee_percent = fee_percent
        # 直接从远往近抓
        self.configuration = ExchangeFetchingConfiguration(
            coin_pair, time_frame, 3, ExchangeFetchingType.FILL_RECENTLY, debug=debug)
        # 策略参数
        self.day_of_week = datetime.today().weekday()
        self.ma_periods = ma_periods
        self.invest_day = day_of_week
        # 交易
        self.__invest_base_amount = invest_base_amount

    def run_task(self):
        self.__fetch_candle()
        # 1. 计算定投倍数
        invest_ratio = self.__calculate_signal()
        # 2. 今天要不要定投（支持多天定投）
        if isinstance(self.invest_day, list):
            days = self.invest_day
        else:
            days = [self.invest_day]
        # 3. 投丫的
        if invest_ratio is not None and invest_ratio > 0 and self.day_of_week in days:
            self.__place_invest_order(invest_ratio)
        else:
            self.recorder.record_summary_log()

    def __get_latest_date(self):
        """For fetching"""
        if self.__df.shape[0] > 0:
            return self.__df[COL_CANDLE_BEGIN_TIME].iloc[-1]
        return datetime.now() - timedelta(days=self.ma_periods + 15)  # 往前多加15天开始

    def __save_df(self, data_df: pd.DataFrame):
        """For fetching"""
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

    def __fetch_candle(self):
        procedure = ExchangeFetchingProcedure(ExchangeFetcher(self.signal_provider),
                                              self.configuration,
                                              None,
                                              self.__get_latest_date,
                                              self.__save_df)

        # Fill to Latest
        procedure.run_task()

        if self.configuration.debug:
            print(self.__df)

        self.recorder.record_procedure("获取 K 线成功")

    def __calculate_signal(self):
        # Calculation
        strategy = AutoBuyCoinStrategy(day_of_week=self.day_of_week,
                                       ma_periods=self.ma_periods)
        signals = strategy.calculate_signals(self.__df, False)
        if self.configuration.debug:
            print(signals[-5:])
        date_string = DateFormatter.convert_local_date_to_string(
            signals['candle_begin_time'][self.__df.index[-1]], "%Y-%m-%d")
        actual_ratio = self._truncate(signals['high_change'][self.__df.index[-1]], self.precision_coefficient)
        advance_ratio = self._truncate(signals['signal'][self.__df.index[-1]], self.precision_coefficient)
        close_price = self._truncate(signals['close'][self.__df.index[-1]], self.precision_price)
        msg = F"""**日期**: {date_string} \n
**计算价格**: {close_price} \n
**市场信号**: {actual_ratio} \n
**定投倍数**: {advance_ratio}"""
        self.recorder.append_summary_log(msg)
        return advance_ratio

    def __place_invest_order(self, ratio):
        # 实际定投数
        invest_amount = ratio * self.__invest_base_amount
        invest_amount = self._truncate(invest_amount, self.precision_amount)
        self.recorder.append_summary_log(
            F'**定投额**({self.__invest_base_amount} x {ratio}): {invest_amount} {self.coin_pair.base_coin.upper()}')
        self.__invest_proccess(invest_amount)

    def __invest_proccess(self, invest_amount):
        """下单流程"""
        # 交易前准备(e.g. 余币宝取钱出来)
        self._prepare_to_buying(invest_amount)
        # 基础币余额
        base_coin_amount = self._fetch_base_coin_balance()
        if base_coin_amount < invest_amount:
            self.recorder.record_summary_log(F'**{self.coin_pair.base_coin.upper()}不足以定投**')
            return
        # 下单
        response = self._place_buying_order(invest_amount)
        if response is None:
            self._rollback_when_order_failed(invest_amount)
            self.recorder.record_summary_log('**下单失败**')
            return
        # order info
        price = self._truncate(response['price'], self.precision_price)
        cost = self._truncate(response['cost'], self.precision_price)
        order_amount = self._truncate(response['amount'], self.precision_amount)
        msg = F"""**下单价格**: {price} \n
**下单总价**: {cost} \n
**买入数量**: {order_amount}
"""
        # 添加记录到数据库
        record = AIPRecord()
        record.exchange = self.trader_provicer.display_name
        record.coin_pair = self.coin_pair.formatted().upper()
        record.cost = cost
        record.amount = order_amount
        record.date = datetime.now()
        record.save()
        # log
        self.recorder.append_summary_log(msg)
        # 收尾工作(e.g. 两种币转回余币宝)
        remaining_base_coin = self._truncate(invest_amount - cost, self.precision_amount)
        self._finishing_aip(remaining_base_coin)
        self.recorder.record_summary_log('**定投成功**')

    def _truncate(self, n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    def _fetch_base_coin_balance(self):
        """基础币余额"""
        balance = self.trader_provicer.ccxt_object_for_fetching.fetch_balance()
        base_coin_balance = balance['free'][self.coin_pair.base_coin]
        return self._truncate(base_coin_balance, self.precision_amount)

    def _fetch_trade_coin_balance(self):
        """目标币余额"""
        balance = self.trader_provicer.ccxt_object_for_fetching.fetch_balance()
        base_coin_balance = balance['free'][self.coin_pair.trade_coin]
        return self._truncate(base_coin_balance, self.precision_amount)

    @ abstractmethod
    def _prepare_to_buying(self, invest_amount):
        """下单前准备，失败自行记录:
        self.recorder.record_summary_log('**划转{}失败**'.format(self.coin_pair.base_coin.upper()))
        """
        raise NotImplementedError("Not implemented")

    @ abstractmethod
    def _place_buying_order(self, invest_amount):
        """下单，成功返回：
        {
          'price': 123,
          'cost': 123,
          'amount': 123
        }"""
        raise NotImplementedError("Not implemented")

    @ abstractmethod
    def _rollback_when_order_failed(self, invest_amount):
        """下单失败后回滚"""
        raise NotImplementedError("Not implemented")

    @ abstractmethod
    def _finishing_aip(self, remaining_base_coin_amount):
        """完成定投后的收尾工作"""
        raise NotImplementedError("Not implemented")
