import math
import pandas as pd
from datetime import datetime, timedelta
from ..generic.spot_fetching import *
from ..util.logger import ProcedureRecorder
from cy_widgets.trader.exchange_trader import *
from cy_widgets.logger.trading import *
from cy_widgets.strategy.exchange.autobuy import *
from cy_widgets.exchange.provider import ExchangeType
from cy_data_access.models.position import *


class OKexAIP:
    """https://www.okex.com/docs/zh/#error-spot"""

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
                 fee_percent=0.0015):
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
        self.recorder.append_summary_log('**{} - 定投**'.format(coin_pair.formatted().upper()))
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
        invest_ratio = self.__calculate_signal()
        if invest_ratio is not None and invest_ratio > 0 and self.invest_day == self.day_of_week:
            self.__place_invest_order(invest_ratio)
        else:
            self.recorder.record_summary_log()

    @staticmethod
    def round_floor(value, digit):
        return float(math.floor(value * digit)) / digit

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
            print(signals[-200:])
        date_string = DateFormatter.convert_local_date_to_string(
            signals['candle_begin_time'][self.__df.index[-1]], "%Y-%m-%d")
        actual_ratio = signals['high_change'][self.__df.index[-1]]
        advance_ratio = signals['signal'][self.__df.index[-1]]
        close_price = signals['close'][self.__df.index[-1]]
        msg = """**日期**: {} \n
**计算价格**: {} \n
**市场信号**: {} \n
**定投倍数**: {}
""".format(date_string, round(close_price, 4), round(actual_ratio, 4), advance_ratio)
        self.recorder.append_summary_log(msg)
        return advance_ratio

    def __place_invest_order(self, ratio):
        # 实际定投数
        invest_amount = ratio * self.__invest_base_amount
        self.recorder.append_summary_log('**定投额**({} x {}): {} {}'.format(self.__invest_base_amount,
                                                                          ratio, invest_amount, self.coin_pair.base_coin.upper()))
        self.__invest_proccess(invest_amount)

    def __invest_proccess(self, invest_amount):
        # ybb->bb
        if not self.__transfer_amount(invest_amount, self.coin_pair.base_coin.lower(), 8, 1):
            self.recorder.record_summary_log('**划转{}失败**'.format(self.coin_pair.base_coin.upper()))
            return
        # balance
        balance = self.trader_provicer.ccxt_object_for_fetching.fetch_balance()
        usdt = balance['free']['USDT']
        # not enough
        if usdt < invest_amount:
            self.recorder.record_summary_log('**{}不足以定投**'.format(self.coin_pair.base_coin.upper()))
        # place order
        logger = TraderLogger(self.trader_provicer.display_name, self.coin_pair.formatted(), 'Spot', self.recorder)
        order = Order(self.coin_pair, invest_amount, 0)
        executor = ExchangeOrderExecutorFactory.executor(self.trader_provicer, order, logger)
        """{'info': {'client_oid': '',
            'created_at': '2020-06-25T07:52:44.171Z',
            'filled_notional': '9.900909395',
            'filled_size': '0.00107953',
            'funds': '',
            'instrument_id': 'BTC-USDT',
            'notional': '',
            'order_id': '5133799533470720',
            'order_type': '0',
            'price': '9263.2',
            'price_avg': '9171.5',
            'product_id': 'BTC-USDT',
            'side': 'buy',
            'size': '0.00107953',
            'state': '2',
            'status': 'filled',
            'timestamp': '2020-06-25T07:52:44.171Z',
            'type': 'limit'},
            'id': '5133799533470720',
            'clientOrderId': '',
            'timestamp': 1593071564171,
            'datetime': '2020-06-25T07:52:44.171Z',
            'lastTradeTimestamp': None,
            'symbol': 'BTC/USDT',
            'type': 'limit',
            'side': 'buy',
            'price': 9263.2,
            'average': 9171.5,
            'cost': 9.900909395,
            'amount': 0.00107953,
            'filled': 0.00107953,
            'remaining': 0,
            'status': 'closed',
            'fee': None,
            'trades': None}"""
        response = executor.handle_long_order_request()
        if response is None:
            self.__transfer_amount(invest_amount, self.coin_pair.base_coin.lower(), 1, 8)
            self.recorder.record_summary_log('**下单失败**')
            return
        # order info
        price = response['average']
        cost = response['cost']
        buy_amount = math.floor(response['filled'] * (1 - self.fee_percent) * 1e8) / 1e8  # *1e8 向下取整再 / 1e8
        msg = """**下单价格**: {} \n
**下单总价**: {} \n
**买入数量**: {}
""".format(round(price, 6), round(cost, 6), round(buy_amount, 8))
        # database record
        record = AIPRecord()
        record.exchange = 'OKEx'
        record.coin_pair = self.coin_pair.formatted().upper()
        record.cost = cost
        record.amount = buy_amount
        record.date = datetime.now()
        record.save()
        # log
        self.recorder.append_summary_log(msg)
        # bb->ybb (RemainingBaseCoin)
        remaining_base_coin = OKexAIP.round_floor(invest_amount - cost, 1e6)  # 保留 6 位
        if remaining_base_coin > 0 and not self.__transfer_amount(remaining_base_coin, self.coin_pair.base_coin.lower(), 1, 8):
            self.recorder.record_summary_log(
                '**划转{}{}失败**'.format(remaining_base_coin, self.coin_pair.base_coin.upper()))
            return
        # bb->ybb (InvestCoin)
        if not self.__transfer_amount(buy_amount, self.coin_pair.trade_coin.lower(), 1, 8):
            self.recorder.record_summary_log('**划转{}{}失败**:{}'.format(buy_amount,
                                                                      self.coin_pair.trade_coin.upper(), order))
            return
        self.recorder.record_summary_log('**定投成功**')

    def __transfer_amount(self, amount, coin, from_type, to_type):
        """ybb和bb互转

        Parameters
        ----------
        coin : str
            usdt/btc/...
        amount : double
            数量
        from_type : int
        to_type : int
            1: bb 8: ybb
        """
        # ybb -> bb
        try:

            # transfer_to = to_type
            # if from_type == 8:
            #     # 先从余币宝转到资金
            #     self.trader_provicer.ccxt_object_for_order.__post_api_account_v3_purchase_redempt({
            #         'currency': coin,
            #         'amount': '{}'.format(amount),
            #         'side': 'redempt'
            #     })
            #     from_type = 6  # 再从资金账户转出到币币
            # elif to_type == 8:
            #     transfer_to = 6  # 要先转到资金
            from_type = 6 if from_type == 8 else from_type
            to_type = 6 if to_type == 8 else to_type
            response = self.trader_provicer.ccxt_object_for_order.account_post_transfer({
                'currency': coin,
                'amount': '{}'.format(amount),
                'type': '0',
                'from': '{}'.format(from_type),
                'to': '{}'.format(to_type)
            })
            # if to_type == 8:
            #     self.trader_provicer.ccxt_object_for_order.__post_api_account_v3_purchase_redempt({
            #         'currency': coin,
            #         'amount': '{}'.format(amount),
            #         'side': 'purchase'
            #     })
            return response['result']
        except Exception as e:
            self.recorder.append_summary_log('{}.{}.划转失败.{}'.format(from_type, to_type, str(e)))
            return False

    def __get_latest_date(self):
        if self.__df.shape[0] > 0:
            return self.__df[COL_CANDLE_BEGIN_TIME].iloc[-1]
        return datetime.now() - timedelta(days=self.ma_periods + 15)  # 往前多加15天开始

    def __save_df(self, data_df: pd.DataFrame):
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
