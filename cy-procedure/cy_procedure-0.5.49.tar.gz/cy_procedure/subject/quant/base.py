from abc import ABC, abstractmethod
from cy_components.utils.coin_pair import *
from cy_components.defines.enums import *
from cy_widgets.exchange.provider import *
from cy_widgets.strategy.exchange import *
from cy_data_access.models.quant import *
from cy_data_access.models.config import *
from cy_data_access.models.market import *
from cy_data_access.models.position import *
from ...util.helper import ProcedureHelper as ph
from ...util.logger import *


class BaseBrickCarrier(ABC):
    """搬砖人基类"""

    _short_sleep_time = 1
    _sleep_when_debug = False  # debug 模式下默认不睡

    def __init__(self, bc_cfg: BrickCarrierCfg, wechat_token, log_type, debug=False, debug_order_proc=False):
        # 整体配置
        self._debug = debug
        self._debug_order_proc = debug_order_proc
        self._bc_cfg = bc_cfg
        self.__wechat_token = wechat_token
        self.__log_type = log_type

        # ccxt 初始化
        ccxt_cfg = CCXTConfiguration.configuration_with_id(bc_cfg.ccxt_cfg_id)
        self._ccxt_provider = CCXTProvider(ccxt_cfg.app_key, ccxt_cfg.app_secret, ExchangeType(ccxt_cfg.e_type), {
            'password': ccxt_cfg.app_pw
        })

        # 取策略
        query = {}
        query["_id"] = {
            u"$in": bc_cfg.strategies
        }
        query["stop"] = {
            u"$ne": True
        }
        self._strategy_cfgs = list(StrategyCfg.objects.raw(query))
        if self._strategy_cfgs is None or len(self._strategy_cfgs) == 0:
            raise ValueError("没有可执行的策略，Exit")

        # 所有策略的币对
        self._symbol_list = list(map(lambda x: x.coin_pair, self._strategy_cfgs))

        # 初始化完成
        self._did_init()

    def __str__(self):
        return "{}\n{}\n{}".format(self._bc_cfg, self._ccxt_provider, self._strategy_cfgs)

    @property
    def _generate_recorder(self):
        return PersistenceRecorder(self.__wechat_token, MessageType.Telegram, self.__log_type)

    def _all_next_run_time_infos(self):
        """获取所有策略下一次执行时间"""
        return {x.identifier: TimeFrame(x.time_interval).next_date_time_point() for x in self._strategy_cfgs}

    def _strategy_from_cfg(self, strategy_cfg: StrategyCfg):
        """CFG -> Strategy Object"""
        strategy: BaseExchangeStrategy = eval(strategy_cfg.strategy_name).strategy_with(strategy_cfg.parameters)
        return strategy

    def _fetch_candle_for_strategy(self, coin_pair: CoinPair, time_frame: TimeFrame, limit, tail=''):
        """取策略需要用的K线"""
        candle_cls = candle_record_class_with_components(self._ccxt_provider.ccxt_object_for_fetching.name, coin_pair, time_frame, tail)
        # 取最后的 limit 条
        pipeline = [{
            '$sort': {
                '_id': -1
            }
        }, {
            "$limit": limit
        }, {
            '$sort': {
                '_id': 1
            }
        }]
        df = pd.DataFrame(list(candle_cls.objects.aggregate(*pipeline)))
        # Tidy candle
        ph.tidy_candle_from_database(df)
        return df

    @ abstractmethod
    def _did_init(self):
        """初始化结束"""
        raise NotImplementedError("Subclass")

    @ abstractmethod
    def perform_procedure(self):
        """主流程"""
        raise NotImplementedError("Subclass")
