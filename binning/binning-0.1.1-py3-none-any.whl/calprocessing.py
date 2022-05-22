
from typing import Any, Callable

from fmpc.utils.LogUtils import get_fmpc_logger
from wares.common.binning.enums import CalType
from wares.common.binning.woe_iv_cal import WoeIvCal
from wares.common.binning.wrap_utils import exec_except, exec_time

logger = get_fmpc_logger(__name__)


class CalProcessing:
    """计算逻辑入口

    Args:
        cal_type (str): 计算类型
        log (Callable): 日志函数

        params (Dict[str, Any]): 处理器参数
        handler (class): 处理器
    """

    def __init__(self,
                 cal_type: str,
                 log: Callable,
                 **kwargs):
        self.cal_type = cal_type
        self.log = log

        self.params = None
        self.handler = None

        self.preprocess(kwargs)

    @exec_time
    @exec_except
    def preprocess(self, kwargs):
        """preprocess"""
        self._check(kwargs)
        self._assemble_params(kwargs)
        self._assemble_handler()

    def _check(self, kwargs):
        """check"""
        if not self.cal_type:
            raise ValueError(f"计算类型cal_type为空，请检查")

        if not isinstance(self.log, Callable):
            raise TypeError(f"日志函数为Callable类型，请检查")

        if not kwargs:
            raise ValueError(f"参数不全，请检查")

    def _assemble_params(self, kwargs):
        """assemble params"""
        self.params = kwargs

    def _assemble_handler(self):
        """assembling handler"""
        if self.cal_type == CalType.WOEIV.name:
            self.handler = WoeIvCal(**self.params)
        else:
            raise TypeError(f"暂不支持此类型计算{self.cal_type}")

    def get_cal_val(self) -> Any:
        """get cal value"""
        return self.handler.get_cal_val(log=self.log)
