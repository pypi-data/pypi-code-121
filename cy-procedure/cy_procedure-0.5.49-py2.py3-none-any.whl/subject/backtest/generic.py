from datetime import datetime
from cy_components.helpers.formatter import DateFormatter as dfr, CandleFormatter as cfr
from cy_components.defines.column_names import *
from cy_components.defines.enums import TimeFrame
from cy_widgets.backtest.strategy import *
from cy_widgets.backtest.helper import *
from cy_data_access.models.backtest import *
from cy_data_access.util.convert import *
from cy_data_access.connection.connect import *
from multiprocessing.pool import Pool
from multiprocessing import Value


class GenericBacktestProcedure:
    """简单回测流程"""

    failed_times = Value('i', 0)
    complete_count = Value('i', 0)
    start_date = datetime.now()

    def __init__(self, task_identifier, time_frames, df, strategy_cls, params, position_func, evaluation_func):
        self.__raw_df = df  # 原始 df
        self.__df = df  # 当前回测在用的 df，方便后面加 df 分割和 resample 用
        self.__raw_time_frames = time_frames
        self.__time_frame = ""

        # ---- K线层参数

        self.__strategy_cls = strategy_cls
        self.__params = params
        self.__position_func = position_func
        self.__evaluation_func = evaluation_func
        self.__task_identifier = task_identifier

        # 总任务数
        self.total_bt_count = len(params) * len(time_frames)

    def unified_exit_handler(self, result, error=None, info=None):
        """单次回测统一结束出口"""
        if not result:
            with self.failed_times.get_lock():
                self.failed_times.value += 1
            print(error, info)
        with self.complete_count.get_lock():
            self.complete_count.value += 1
            print('{}% {}/{} {}'.format(round(self.complete_count.value / self.total_bt_count * 100, 2),
                                        self.complete_count.value, self.total_bt_count,
                                        datetime.now() - self.start_date))

    def __result_handler(self, context, position_df, evaluated_res, strategy, error_des):
        """单次回测结束"""
        try:
            if error_des is not None:
                self.unified_exit_handler(False, '回测计算过程失败', error_des)
            else:
                param_identifier = context['param_identifier']
                # 简要数据
                connect_db_env(db_name=DB_BACKTEST)
                overview = BacktestOverview(task_identifier=self.__task_identifier,
                                            param_identifier=param_identifier,
                                            equity_curve=evaluated_res.get('累积净值', 0),
                                            statics_info=evaluated_res)
                # 保存总览数据
                overview.save()
                self.unified_exit_handler(True)
        except Exception as e:
            print(str(e))
            self.unified_exit_handler(False, '回测结果处理失败', context)

    def calculation(self, param):
        """单次回测开始"""
        try:
            connect_db_env(db_name=DB_BACKTEST)
            strategy = self.__strategy_cls(**param)
            param_str = ";".join(["{}:{}".format(key, param[key]) for key in sorted(param.keys())])
            start_date = dfr.convert_local_date_to_string(self.__df.iloc[0][COL_CANDLE_BEGIN_TIME], "%Y%m%d")
            end_date = dfr.convert_local_date_to_string(self.__df.iloc[-1][COL_CANDLE_BEGIN_TIME], "%Y%m%d")
            param_identifier = "{}|{}|{}|{}".format(
                strategy.name, param_str, self.__time_frame, "{},{}".format(start_date, end_date))

            if len(list(BacktestOverview.objects.raw({'task_identifier': self.__task_identifier,
                                                      'param_identifier': param_identifier}))) > 0:
                print("{} 已存在，跳过".format(param_identifier))
                self.unified_exit_handler(True)
                return None

            context = {
                'param_identifier': param_identifier
            }

            bt = StrategyBacktest(self.__df.copy(), strategy, self.__position_func,
                                  self.__evaluation_func, self.__result_handler, context)
            return bt.perform_test()
        except Exception as e:
            self.unified_exit_handler(False, '回测执行失败', str(param))
            print(str(e))
            return None

    def perform_test_proc(self, processes=2):
        for time_frame in self.__raw_time_frames:
            self.__time_frame = time_frame

            tf = TimeFrame(time_frame)
            self.__df = cfr.resample(self.__raw_df, tf.rule_type)

            # 到这里 self.__df / self.__time_frame 都是策略的了
            with Pool(processes=processes) as pool:
                pool.map(self.calculation, self.__params)
