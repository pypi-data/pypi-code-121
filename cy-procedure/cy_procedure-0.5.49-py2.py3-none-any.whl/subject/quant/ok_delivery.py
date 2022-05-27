import random
import traceback
import pytz
from multiprocessing.pool import Pool
from .base import *
from ..exchange.okex import *


class OKDeliveryBC(BaseBrickCarrier):
    """OK 合约单账户实盘执行流程"""

    __symbol_info_columns = ['账户权益', '持仓方向', '持仓量', '持仓收益率', '持仓收益', '持仓均价', '当前价格', '最大杠杆']
    __symbol_info_df = None
    __symbol_index_mapping = None
    __next_run_time = None

    def _did_init(self):
        """初始化结束，父类调用"""
        self.__ok_handler = OKExHandler(self._ccxt_provider)
        # {'eth-usdt': 'ETH-USDT-210326'}
        self.__symbol_index_mapping = {name: coin_pair for name in coin_value_table for coin_pair in self._symbol_list if (name + '-').upper() in coin_pair.upper()}
        # {'ETH-USDT-210326': 'eth-usdt'}
        self.__symbol_index_reverse_mapping = {self.__symbol_index_mapping[name]: name for name in self.__symbol_index_mapping}

    def __reset_infos(self):
        self.__symbol_info_df = pd.DataFrame(index=self._symbol_list, columns=self.__symbol_info_columns)  # 转化为dataframe

    def perform_procedure(self):
        """主流程"""
        while True:
            self.__reset_infos()
            self.__symbol_info_df = self.__ok_handler.update_symbol_info(self.__symbol_info_df, self._symbol_list, self.__symbol_index_mapping)
            # 把标的转为具体
            print('\nsymbol_info:\n', self.__symbol_info_df, '\n')
            # 计算每个策略的下次开始时间
            all_next_time_infos = self._all_next_run_time_infos()
            # 取最小的作为下次开始
            self.__next_run_time = min(all_next_time_infos.values())
            # 非 Debug || Debug 模式也等 = 等待
            if not self._debug or self._sleep_when_debug:
                print('策略执行时间:')
                for nt_key in all_next_time_infos:
                    print(nt_key, list(filter(lambda x: x.identifier == nt_key, self._strategy_cfgs))[0].coin_pair, ': ', all_next_time_infos[nt_key])
                print('下次执行时间: ', self.__next_run_time)
                # 取最近的，等等等
                time.sleep(max(0, (self.__next_run_time - datetime.now()).seconds))
                while True:  # 在靠近目标时间时
                    if datetime.now() > self.__next_run_time:
                        break
            if self._debug:
                # 测试直接全运行
                to_run_strategie_ids = all_next_time_infos.keys()
            else:
                # 到时间的策略进入流程
                to_run_strategie_ids = [s_id for s_id in all_next_time_infos.keys() if all_next_time_infos[s_id] == self.__next_run_time]
            with Pool(processes=2) as pool:
                pool.map(self.single_strategy_procedure, to_run_strategie_ids)
            # 本次循环结束
            print('\n', '-' * 20, '本次循环结束，%f秒后进入下一次循环' % 10, '-' * 20, '\n\n')
            time.sleep(10)

    def single_strategy_procedure(self, strategy_id):
        """并行线程，单个策略流程"""
        try:
            recorder = self._generate_recorder  # 拉一个记录员来记录搬砖现场
            cfg: StrategyCfg = list(filter(lambda x: x.identifier == strategy_id, self._strategy_cfgs))[0]
            strategy: BaseExchangeStrategy = self._strategy_from_cfg(cfg)
            current_time = self.__next_run_time.astimezone(tz=pytz.utc)  # 用来过滤最近一根K线
            recorder.append_summary_log("**{}-{}-{}**".format(cfg.strategy_name, cfg.coin_pair, cfg.identifier))
            time.sleep(2)
            # 取K线
            while True:
                time_frame = TimeFrame(cfg.time_interval)
                candle_df = self._fetch_candle_for_strategy(ContractCoinPair.coin_pair_with(cfg.coin_pair, '-'),
                                                            time_frame,
                                                            limit=strategy.candle_count_for_calculating)
                # 用来计算信号的，把最新这根删掉
                cal_signal_df = candle_df[candle_df.candle_begin_time < current_time]
                delta = current_time - cal_signal_df.iloc[-1].candle_begin_time.tz_convert(pytz.utc)
                tolerance = 9 if self._debug else 2
                if time_frame.value.endswith('m'):
                    has_last = delta.total_seconds() < int(time_frame.value[:-1]) * 60 * tolerance
                elif time_frame.value.endswith('h'):
                    has_last = delta.total_seconds() < int(time_frame.value[:-1]) * 60 * 60 * tolerance
                else:
                    raise ValueError('time_interval不以m或者h结尾，出错，程序exit')
                if not has_last:
                    self._generate_recorder.record_exception('{} 最后 K 线时间: {}'.format(cfg.coin_pair, cal_signal_df.iloc[-1].candle_begin_time))
                    if datetime.now() > self.__next_run_time + timedelta(minutes=2):
                        raise ValueError('{} 时间超过2分钟，放弃，返回空数据'.format(cfg.coin_pair))
                    else:
                        print('{} 没有最新数据'.format(cfg.coin_pair), datetime.now())
                        time.sleep(5)
                else:
                    break
            # 策略信号
            signals = self.__calculate_signal(strategy, cal_signal_df, cfg.coin_pair, strategy_id=strategy_id)
            recorder.append_summary_log("**信号**: {}".format(signals))
            # 假信号逻辑
            # signals = self.__real_signal_random(cfg.coin_pair)
            print('{} 信号'.format(cfg.coin_pair), signals)
            # 策略下单
            order_infos = None
            if signals and not self._debug:  # 测试模式下不进
                signal_price = candle_df.iloc[-1].close  # 最后一根K线的收盘价作为信号价
                holding = self.__symbol_info_df.at[cfg.coin_pair, "持仓量"]
                equity = self.__symbol_info_df.at[cfg.coin_pair, "账户权益"]
                leverage = min(float(cfg.leverage), float(self.__symbol_info_df.at[cfg.coin_pair, "最大杠杆"]))
                # 下单逻辑
                retry_times = 20
                while True:
                    try:
                        order_ids = self.__ok_handler.okex_future_place_order(self.__symbol_index_reverse_mapping[cfg.coin_pair], cfg.coin_pair, signals, signal_price, holding, equity, leverage)
                        break
                    except Exception as e:
                        if retry_times <= 0:
                            raise ValueError(f'尝试下单次数真的太多了，退出({cfg.coin_pair}, {signals})')
                        else:
                            self._generate_recorder.record_exception(f'下单失败，稍后重试({cfg.coin_pair}, {signals})')
                            retry_times -= 1
                            time.sleep(45)

                print('{} 下单记录：\n'.format(cfg.coin_pair), order_ids)
                # 更新订单信息，查看是否完全成交
                time.sleep(self._short_sleep_time)  # 休息一段时间再更新订单信息
                order_infos = self.__ok_handler.update_future_order_info(cfg.coin_pair, order_ids)
                print('更新下单记录：', '\n', order_infos)
            # 订单保存
            if order_infos is not None:
                # 记录员登记订单信息
                recorder.append_summary_log("**下单信息**:")
                for order_id in order_infos:
                    order = StrategyOrder.order_with(strategy_id, order_id)
                    order.date = datetime.now().astimezone()
                    order.order_desc = order_infos[order_id]
                    order.save()
                    # 取订单各种状态
                    for o_inner_key in order_infos[order_id]:
                        recorder.append_summary_log("**{}**: {}".format(o_inner_key, order_infos[order_id][o_inner_key]))
            else:
                '''
                {'BTC-USDT-210326': {'账户权益': '50', '持仓方向': 0, '持仓量': nan, '持仓收益率': nan, '持仓收益': nan, '持仓均价': nan, '当前价格': nan, '最大杠杆': nan}}
                {'ETH-USDT-210326': {'账户权益': '61.61780297', '持仓方向': 0, '持仓量': nan, '持仓收益率': nan, '持仓收益': nan, '持仓均价': nan, '当前价格': 760.88, '最大杠杆': 10.0}}
                '''
                # 没有订单信息，记录一下本周期的仓位状态
                info_dict = self.__symbol_info_df.loc[[cfg.coin_pair], :].T.to_dict()[cfg.coin_pair]
                recorder.append_summary_log("**账户权益**: {}".format(info_dict['账户权益']))
                recorder.append_summary_log("**持仓方向**: {}".format(info_dict['持仓方向']))
                if info_dict['持仓方向'] != 0:
                    # 非空仓，记录其他的
                    key_names = ['持仓量', '持仓收益率', '持仓收益', '持仓均价', '当前价格']
                    for name in key_names:
                        recorder.append_summary_log("**{}**: {}".format(name, info_dict[name]))
            recorder.record_summary_log("{}".format(datetime.now()))
        except Exception as e:
            self._generate_recorder.record_exception("策略({})中断: {}".format(strategy_id, traceback.format_exc()))

    def __real_signal_random(self, coin_pair_str):
        """
        随机发出交易信号
        :param df:
        :param now_pos:
        :param avg_price:
        :param para:
        :return:
        """

        now_pos = self.__symbol_info_df.at[coin_pair_str, '持仓方向']  # 当前持仓方向

        target_pos = None
        symbol_signal = None

        r = random.random()
        if r <= 0.25:
            target_pos = 1
        elif r <= 0.5:
            target_pos = -1
        elif r <= 0.75:
            target_pos = 0

        # 根据目标仓位和实际仓位，计算实际操作，"1": "开多"，"2": "开空"，"3": "平多"， "4": "平空"
        if now_pos == 1 and target_pos == 0:  # 平多
            symbol_signal = [3]
        elif now_pos == -1 and target_pos == 0:  # 平空
            symbol_signal = [4]
        elif now_pos == 0 and target_pos == 1:  # 开多
            symbol_signal = [1]
        elif now_pos == 0 and target_pos == -1:  # 开空
            symbol_signal = [2]
        elif now_pos == 1 and target_pos == -1:  # 平多，开空
            symbol_signal = [3, 2]
        elif now_pos == -1 and target_pos == 1:  # 平空，开多
            symbol_signal = [4, 1]

        self.__symbol_info_df.at[coin_pair_str, '信号时间'] = datetime.now()  # 计算产生信号的时间

        return symbol_signal

    def __calculate_signal(self, strategy: BaseExchangeStrategy, candle_data, coin_pair_str, strategy_id):
        """计算信号，根据持仓情况给出最终信号（止盈止损情况后面加"""

        # 策略保存的信息
        strategy_position = StrategyPosition.position_with(strategy_id)

        def saver(strategy_info):
            # 保存方法
            strategy_position.strategy_info = strategy_info
            strategy_position.save()

        # 赋值相关数据
        df = candle_data.copy()  # 最新数据
        now_pos = self.__symbol_info_df.at[coin_pair_str, '持仓方向']  # 当前持仓方向
        # avg_price = self.__symbol_info_df.at[coin_pair_str, '持仓均价']  # 当前持仓均价（后面用来控制止盈止损

        print('now pos', now_pos)
        # 需要计算的目标仓位
        target_pos = None
        symbol_signal = None

        # 不够计算
        if not strategy.available_to_calculate(df):
            print(df.shape[0])
            raise ValueError(f'K 线数量无法计算信号, {strategy.candle_count_for_calculating}, {df.shape[0]}')

        # 根据策略计算出目标交易信号。
        if not df.empty:  # 当原始数据不为空的时候
            target_pos = strategy.calculate_realtime_signals(df, debug=self._debug, position_info=strategy_position.strategy_info, position_info_save_func=saver)

        # 根据目标仓位和实际仓位，计算实际操作，"1": "开多"，"2": "开空"，"3": "平多"， "4": "平空"
        if now_pos == 1 and target_pos == 0:  # 平多
            symbol_signal = [3]
        elif now_pos == -1 and target_pos == 0:  # 平空
            symbol_signal = [4]
        elif now_pos == 0 and target_pos == 1:  # 开多
            symbol_signal = [1]
        elif now_pos == 0 and target_pos == -1:  # 开空
            symbol_signal = [2]
        elif now_pos == 1 and target_pos == -1:  # 平多，开空
            symbol_signal = [3, 2]
        elif now_pos == -1 and target_pos == 1:  # 平空，开多
            symbol_signal = [4, 1]

        self.__symbol_info_df.at[coin_pair_str, '信号时间'] = datetime.now()  # 计算产生信号的时间

        return symbol_signal
