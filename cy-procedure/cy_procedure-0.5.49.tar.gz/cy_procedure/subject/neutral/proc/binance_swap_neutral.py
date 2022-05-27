import pytz
import time
import traceback
import json
import multiprocessing as mp
from random import randrange
from datetime import datetime, timedelta
from multiprocessing.pool import Pool
from cy_components.defines.enums import *
from cy_widgets.exchange.provider import *
from cy_widgets.strategy.neutral import *
from cy_data_access.models.quant import *
from cy_data_access.models.config import *
from cy_data_access.models.market import *
from cy_data_access.models.position import *
from cy_data_access.util.convert import *
from ...exchange.binance import *
from ....util.helper import ProcedureHelper as ph
from ....util.logger import *

pd.options.display.max_columns = None


class BinanceSwapNeutral:

    _short_sleep_time = 1
    _long_sleep_time = 10
    _sleep_when_debug = False  # debug 模式下默认不睡

    _update_day_interval = 1  # 每隔多少天更新一次trade_usdt。其中trade_usdt为用于交易选币策略的总资金。
    _update_hour = 11         # 当当天要更新trade_usdt时，在当天的几点进行更新。

    def __init__(self, bc_cfg: BrickCarrierCfg, wechat_token, log_type, debug=False):
        # 整体配置
        self._debug = debug
        self._bc_cfg = bc_cfg
        self.__wechat_token = wechat_token
        self.__log_type = log_type

        # ccxt 初始化
        ccxt_cfg = CCXTConfiguration.configuration_with_id(bc_cfg.ccxt_cfg_id)
        self._ccxt_provider = CCXTProvider(ccxt_cfg.app_key, ccxt_cfg.app_secret, ExchangeType(ccxt_cfg.e_type), {
            'password': ccxt_cfg.app_pw,
            'defaultType': 'future'
        })
        self.__binance_handler = BinanceHandler(self._ccxt_provider)

        # 取策略, 只支持一个策略
        query = {}
        query["_id"] = {
            u"$in": bc_cfg.strategies
        }
        query["stop"] = {
            u"$ne": True
        }
        self._strategy_cfg: StrategyCfg = list(StrategyCfg.objects.raw(query))[0]
        strategy_name = self._strategy_cfg.strategy_name
        parameters = self._strategy_cfg.parameters

        self._strategy: NeutralStrategyBase = eval(strategy_name)(parameters)

        # 币对
        self.__fetch_symbol_list()

    @property
    def _generate_recorder(self):
        if self._debug:
            return SimpleRecorder()
        else:
            return PersistenceRecorder(self.__wechat_token, MessageType.Telegram, self.__log_type)

    def __fetch_symbol_list(self):
        # 更新一次 Symbols
        self.__symbol_list_with_sep = self.__binance_handler.all_usdt_swap_symbols()
        self.__symbol_list = list(map(lambda x: x.replace("/", ''), self.__symbol_list_with_sep))

    def __cal_old_and_new_trade_usdt(self):
        """ 每隔一段时间修改一下trade_usdt """
        strategy_id = self._strategy_cfg.identifier
        strategy_position = StrategyPosition.position_with(strategy_id)
        """
           {
               'usdt': {
                   20200101: 123
                   20200102: 234
               }
           }
           """
        info = strategy_position.strategy_info
        if info is not None and len(info) > 0 and 'usdt' in info:
            usdt_records = info['usdt']
            # 最后一条数量
            last_trade_usdt = usdt_records[sorted(usdt_records)[-1]]
            # 满足更新条件，需要更新trade_usdt
            if (datetime.now() - datetime(2000, 1, 1)).days % self._update_day_interval == 0 and datetime.now().hour == self._update_hour:
                trade_usdt_new = self.__binance_handler.fetch_binance_swap_equity()  # 最新的账户净值
                trade_usdt_old = last_trade_usdt  # 本地记录的trade_usdt
            # 不满足更新条件，使用本地的trade_usdt
            else:
                trade_usdt_new = last_trade_usdt
                trade_usdt_old = last_trade_usdt

        # 本地不存在trade_usdt_history.txt文件
        else:
            trade_usdt_new = self.__binance_handler.fetch_binance_swap_equity()  # 读取币安账户最新的trade_usdt
            trade_usdt_old = trade_usdt_new

        print('trade_usdt_old：', trade_usdt_old, 'trade_usdt_new：', trade_usdt_new, '\n')
        return trade_usdt_old, trade_usdt_new

    def __update_trade_usdt_if_needed(self, run_time, last_trade_usdt):
        """更新到数据库"""
        if (run_time - datetime(2000, 1, 1)).days % self._update_day_interval == 0 and datetime.now().hour == self._update_hour:
            print('开始更新trade_usdt')
            strategy_id = self._strategy_cfg.identifier
            strategy_position = StrategyPosition.position_with(strategy_id)
            """
            {
                'usdt': {
                    20200101: 123
                    20200102: 234
                }
            }
            """
            info = strategy_position.strategy_info
            time_key = DateFormatter.convert_local_date_to_string(run_time, '%Y-%m-%d')
            if info is not None and len(info) > 0 and 'usdt' in info:
                usdt_records = info['usdt']
                usdt_records[time_key] = last_trade_usdt
                info['usdt'] = usdt_records
            else:
                if info is None:
                    info = dict()
                info['usdt'] = {
                    time_key: last_trade_usdt
                }
            # 保存到数据库
            strategy_position.strategy_info = info
            strategy_position.save()

    def __cal_strategy_trade_usdt(self, trade_usdt_new, trade_usdt_old):
        """ 计算分配的资金 """
        df = pd.DataFrame()
        hold_period = self._strategy.hold_period
        selected_coin_num = self._strategy.select_coin_num

        offset_num = int(hold_period[:-1])
        for offset in range(offset_num):
            df.loc[f'{hold_period}_{offset}H', '策略分配资金_旧'] = trade_usdt_old * self._strategy.leverage / 2 / offset_num / selected_coin_num
            df.loc[f'{hold_period}_{offset}H', '策略分配资金_新'] = trade_usdt_new * self._strategy.leverage / 2 / offset_num / selected_coin_num

        df.reset_index(inplace=True)
        df.rename(columns={'index': 'key'}, inplace=True)

        return df

    def __cal_order_amount(self, symbol_info, select_coin, strategy_trade_usdt, run_time):
        """ 计算每个币种的实际下单量，并且聚会汇总，放到symbol_info变量中 """
        # 合并每个策略分配的资金
        select_coin = pd.merge(left=select_coin, right=strategy_trade_usdt, how='left')

        # 将策略选币时间end_time与当天的凌晨比较，越过凌晨时刻则用本周期的资金，否则用上周期资金
        select_coin['策略分配资金'] = np.where(select_coin['e_time'] >= run_time.replace(hour=self._update_hour).astimezone(tz=pytz.utc), select_coin['策略分配资金_新'], select_coin['策略分配资金_旧'])
        # 计算下单量
        select_coin['目标下单量'] = select_coin['策略分配资金'] / select_coin['close'] * select_coin['方向']
        print(select_coin[['key', 's_time', 'symbol', '方向', '策略分配资金_旧', '策略分配资金_新', '策略分配资金', '目标下单量']], '\n')

        # 对下单量进行汇总
        symbol_info['目标下单量'] = select_coin.groupby('symbol')[['目标下单量']].sum()
        symbol_info['目标下单量'].fillna(value=0, inplace=True)
        symbol_info['目标下单份数'] = select_coin.groupby('symbol')[['方向']].sum()
        symbol_info['实际下单量'] = symbol_info['目标下单量'] - symbol_info['当前持仓量']
        # 删除实际下单量为0的币种
        symbol_info = symbol_info[symbol_info['实际下单量'] != 0]
        return symbol_info, select_coin

    def __sleep_to_next_run_time(self, next_run_time):
        """等到下一次"""
        # 非 Debug || Debug 模式也等 = 等待
        if not self._debug or self._sleep_when_debug:
            print('下次执行时间: ', next_run_time)
            # 取最近的，等等等
            time.sleep(max(0, (next_run_time - datetime.now()).seconds))
            while True:  # 在靠近目标时间时
                if datetime.now() > next_run_time:
                    break

    def __fetch_all_candle(self, limit, run_time):
        """取所有币的K线"""
        # 创建参数列表
        arg_list = [(CoinPair.coin_pair_with(symbol), TimeFrame('1h'), limit, run_time) for symbol in self.__symbol_list_with_sep]
        # 多进程获取数据
        s_time = time.time()
        with Pool(processes=mp.cpu_count()) as pl:
            # 利用starmap启用多进程信息
            result = pl.starmap(self.fetch_candle_for_strategy, arg_list)

        df = dict(result)
        df = {x: df[x] for x in df if x is not None}
        print('获取所有币种K线数据完成，花费时间：', time.time() - s_time, len(df))
        return df

    def fetch_candle_for_strategy(self, coin_pair: CoinPair, time_frame: TimeFrame, limit, run_time):
        """取策略需要用的K线"""
        candle_cls = candle_record_class_with_components(self._ccxt_provider.ccxt_object_for_fetching.name, coin_pair, time_frame, '_swap')
        # 取最后的 limit 条
        pipeline = [{
            '$sort': {
                '_id': -1
            }
        }, {
            '$match': {
                'volume': {
                    '$gt': 0
                }
            }
        }, {
            "$limit": limit + 10
        }, {
            '$sort': {
                '_id': 1
            }
        }]
        df = pd.DataFrame(list(candle_cls.objects.aggregate(*pipeline)))

        # 数据不够，不要了
        symbol = coin_pair.formatted().upper()
        if df is None or df.shape[0] < limit:
            print(f'{symbol} 数据太少')
            return None, None

        # Tidy candle
        ph.tidy_candle_from_database(df)

        # 删除runtime那行的数据，如果有的话
        candle_begin_time = run_time.astimezone(tz=pytz.utc)
        df = df[df['candle_begin_time'] < candle_begin_time]

        if df.shape[0] < limit:
            return None, None

        # 离现在超过2小时，不要了
        delta = candle_begin_time - df.iloc[-1].candle_begin_time.tz_convert(pytz.utc)
        tolerance = 999 if self._debug else 3
        if delta.total_seconds() >= 60 * 60 * tolerance:
            print(f'{symbol} 没有最近的K线, {delta.total_seconds()}')
            return None, None

        df['symbol'] = symbol.replace("/", '')
        # print('结束获取k线数据：', symbol, datetime.now())

        return symbol, df

    def perform_proc(self):
        while True:
            try:
                recorder = self._generate_recorder
                recorder.append_summary_log("**{}**".format(self._strategy.display_name))
                # ===== 获取账户的实际持仓
                symbol_info = self.__binance_handler.update_symbol_info(self.__symbol_list)
                # ===== 等待下次执行 (固定1h)
                next_run_time = TimeFrame('1h').next_date_time_point()
                print('下次执行时间:', next_run_time)
                self.__sleep_to_next_run_time(next_run_time)
                # ===== 计算旧的和新的策略分配资金
                trade_usdt_old, trade_usdt_new = self.__cal_old_and_new_trade_usdt()
                recorder.append_summary_log("**账户净值**: {} USDT".format(trade_usdt_new))
                # ===== 计算每个策略分配的交易资金
                strategy_trade_usdt = self.__cal_strategy_trade_usdt(trade_usdt_new, trade_usdt_old)
                print(strategy_trade_usdt)
                retry_times = 60
                # 核心逻辑添加重试机制
                while True:
                    try:
                        # ===== 取 K 线
                        limit = self._strategy.candle_count_4_cal_factor
                        candle_df_dict = self.__fetch_all_candle(limit, next_run_time)
                        # 太少币种
                        if len(candle_df_dict) < 10:
                            self._generate_recorder.record_exception(f'可选的币太少了，{len(candle_df_dict)}')
                            time.sleep(self._long_sleep_time)
                            continue
                        # ===== 选币
                        select_coin_factor_df = self._strategy.cal_factor_and_select_coins(candle_df_dict, next_run_time)
                        # ===== 计算选中币种的实际下单量
                        symbol_info, select_coin_df = self.__cal_order_amount(symbol_info, select_coin_factor_df, strategy_trade_usdt, next_run_time)
                        # ===== 逐个下单
                        symbol_last_price = self.__binance_handler.fetch_binance_ticker_data()  # 获取币种的最新价格
                        if not self._debug:
                            self.__binance_handler.place_order(symbol_info, symbol_last_price)  # 下单
                        break
                    except Exception as _:
                        self._generate_recorder.record_exception(self._strategy.display_name + traceback.format_exc())
                        if retry_times > 0:
                            retry_times -= 1
                            time.sleep(15)
                        else:
                            self._generate_recorder.record_exception(self._strategy.display_name + ' 失败太多次，本周期放弃')
                            break

                # ===== 最后一次选币保存
                select_coin_df = select_coin_df[['key', 's_time', 'e_time', 'symbol', '方向', '策略分配资金', '目标下单量']]
                grouped_df = select_coin_df.groupby('s_time')
                last_selection_df = list(grouped_df)[-1][1]
                last_selection_df['strategy'] = self._strategy.display_name
                if not self._debug:
                    connect_db_and_save_json_list(DB_POSITION, CN_NEUTRAL_SELECTION, convert_simple_df_to_json_list(last_selection_df), False)
                # ===== 推送本次选币结果
                s = last_selection_df['symbol']
                p = last_selection_df['方向']
                a = last_selection_df['目标下单量']
                l = list(zip(s, p, a))
                recorder.append_summary_log("**本次选币**: \n{}".format('\n'.join([f'{x[0]}: {x[1]} ({round(x[2], 4)})' for x in l])))
                recorder.append_summary_log(f"**选币时间**: {datetime.now()}")  # 记录选币时间
                # ===== 按需更新 Trade usdt
                time.sleep(self._short_sleep_time)  # 下单之后休息一段时间
                self.__update_trade_usdt_if_needed(next_run_time, trade_usdt_new)
                # ===== 推送通知
                recorder.record_summary_log()
                # ===== 更新一次 Symbols ======
                self.__fetch_symbol_list()
                print('\n', '-' * 20, '本次循环结束，%f秒后进入下一次循环' % self._long_sleep_time, '-' * 20, '\n\n')
                time.sleep(self._long_sleep_time)
            except Exception as _:
                self._generate_recorder.record_exception(traceback.format_exc())
                time.sleep(self._short_sleep_time)
