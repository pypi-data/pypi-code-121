import talib
import numpy as np
import pandas as pd


class sma:
    """简单移动平均线"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.SMA(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class ema:
    """指数平均数指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.EMA(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class kama:
    """考夫曼的自适应移动平均线"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.KAMA(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class wma:
    """加权移动平均数"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.WMA(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class cmo:
    """钱德动量摆动指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.CMO(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class mom:
    """动量线"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.MOM(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class roc:
    """变动率指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.ROC(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class rocr:
    """ROCR的移动平均"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.ROCR(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class rocp:
    """roc真假率"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.ROCP(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class rocr_100:
    """ROCR的移动平均"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.ROCR100(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class trix:
    """三重指数平滑平均线"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.TRIX(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class obv:
    """能量潮"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.OBV(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class rsi:
    """相对强弱指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.RSI(self.__price_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class apo:
    """价格振荡器指数"""

    def __init__(
        self, 
        init_count: int, 
        fast_period: int, 
        slow_period: int, 
        matype: int = 0, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert fast_period > 1 and slow_period > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__fast_period = fast_period
        self.__slow_period = slow_period
        self.__matype = matype

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.APO(
                self.__price_cache, 
                self.__fast_period, 
                self.__slow_period, 
                self.__matype
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class ppo:
    """计算百分比表示的相对差异"""

    def __init__(
        self, 
        init_count: int, 
        fast_period: int, 
        slow_period: int, 
        matype: int = 0, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert fast_period > 1 and slow_period > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__fast_period = fast_period
        self.__slow_period = slow_period
        self.__matype = matype

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.PPO(
                self.__price_cache, 
                self.__fast_period, 
                self.__slow_period, 
                self.__matype
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class std:
    """成交量标准差"""

    def __init__(
        self, 
        init_count: int, 
        window: int, 
        nbdev: int = 1, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window
        self.__nbdev = nbdev

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.STDDEV(self.__price_cache, self.__window, self.__nbdev)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class cci:
    """顺势指标"""

    def __init__(
        self, 
        init_count: int, 
        window: int, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.CCI(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class atr:
    """平均真实波动范围"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.ATR(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class natr:
    """标准atr"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.NATR(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class macd:
    """异同移动平均线"""

    def __init__(
        self, 
        init_count: int, 
        fast_period: int,
        slow_period: int,
        signal_period: int, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert fast_period > 1 and slow_period > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__fast_period = fast_period
        self.__slow_period = slow_period
        self.__signal_period = signal_period

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> (float, float, float):
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            macd, signal, hist = talib.MACD(
                self.__close_cache, 
                self.__fast_period, 
                self.__slow_period, 
                self.__signal_period
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(macd[-1], signal[-1], hist[-1])

            return macd[-1], signal[-1], hist[-1]
        return None


class adx:
    """或平均趋向指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.ADX(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class adxr:
    """平均方向指数评估"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.ADXR(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class dx:
    """平均趋势指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.DX(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class minus_di:
    """DMI 中的DI指标 负方向指标 下升动向值"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.MINUS_DI(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class plus_di:
    """DMI 中的DI指标 正方向指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.PLUS_DI(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class willr:
    """威廉指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.WILLR(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class trange:
    """波动率指标"""

    def __init__(self, init_count: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.TRANGE(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class ultosc:
    """十日平均价"""

    def __init__(
        self, 
        init_count: int, 
        time_period1: int = 7,
        time_period2: int = 14,
        time_period3: int = 28,
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 保存参数
        self.__time_period1 = time_period1
        self.__time_period2 = time_period2
        self.__time_period3 = time_period3

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            result = talib.ULTOSC(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache,
                self.__time_period1,
                self.__time_period2,
                self.__time_period3
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class boll:
    """布林通道"""

    def __init__(
        self, 
        init_count: int, 
        window: int, 
        dev: float, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window
        self.__dev = dev

        # 价格序列缓存
        self.__price_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, price: float) -> (float, float):
        """添加新的价格数据"""

        # 添加数据
        self.__price_cache[:-1] = self.__price_cache[1:]
        self.__price_cache[-1] = price

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            mid_list = talib.SMA(self.__price_cache, self.__window)
            std_list = talib.STDDEV(self.__price_cache, self.__window, 1)

            mid = mid_list[-1]
            std = std_list[-1]

            up = mid + std * self.__dev
            down = mid - std * self.__dev

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(up, down)

            return up, down
        return None


class keltner:
    """肯特纳通道"""

    def __init__(
        self, 
        init_count: int, 
        window: int, 
        dev: float, 
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window
        self.__dev = dev

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float) -> (float, float):
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__close_cache) >= self.__init_count:
            mid_list = talib.SMA(
                self.__close_cache, 
                self.__window
            )
            atr_list = talib.ATR(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache, 
                self.__window
            )

            mid = mid_list[-1]
            atr = atr_list[-1]

            up = mid + atr * self.__dev
            down = mid - atr * self.__dev

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(up, down)

            return up, down
        return None


class donchian:
    """唐安奇通道"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, high: float, low: float) -> (float, float):
        """添加新的价格数据"""

        # 添加数据
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            up = talib.MAX(self.__high_cache, self.__window)
            down = talib.MIN(self.__low_cache, self.__window)

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(up[-1], down[-1])

            return up[-1], down[-1]
        return None


class aroon:
    """阿隆指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, high: float, low: float) -> (float, float):
        """添加新的价格数据"""

        # 添加数据
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            aroon_down, aroon_up = talib.AROON(
                self.__high_cache, 
                self.__low_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(aroon_up[-1], aroon_down[-1])

            return aroon_up[-1], aroon_down[-1]
        return None


class aroonosc:
    """阿隆震荡线"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.AROONOSC(
                self.__high_cache, 
                self.__low_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class minus_dm:
    """DMI 中的DM指标 负方向指标 下升动向值"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.MINUS_DM(
                self.__high_cache, 
                self.__low_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class plus_dm:
    """DMI 中的DM指标 正方向指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.PLUS_DM(
                self.__high_cache, 
                self.__low_cache, 
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class mfi:
    """资金流量指标"""

    def __init__(self, init_count: int, window: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"
        assert window > 1, f"移动平均线的计算窗口必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 移动平均线计算窗口
        self.__window = window

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)
        self.__volume_cache = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float, volume: int) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low
        self.__volume_cache[:-1] = self.__volume_cache[1:]
        self.__volume_cache[-1] = volume

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.MFI(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache,
                self.__volume_cache,
                self.__window
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class ad:
    """集散量线"""

    def __init__(self, init_count: int, call_back=None):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"

        # 初始计数
        self.__init_count = init_count

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)
        self.__volume_cache = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float, volume: int) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low
        self.__volume_cache[:-1] = self.__volume_cache[1:]
        self.__volume_cache[-1] = volume

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.AD(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache,
                self.__volume_cache
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class adosc:
    """集散量震荡线"""

    def __init__(
        self, 
        init_count: int, 
        fast_period: int,
        slow_period: int,
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"

        # 初始计数
        self.__init_count = init_count
        self.__fast_period = fast_period
        self.__slow_period = slow_period

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)
        self.__volume_cache = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, close: float, high: float, low: float, volume: int) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low
        self.__volume_cache[:-1] = self.__volume_cache[1:]
        self.__volume_cache[-1] = volume

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.ADOSC(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache,
                self.__volume_cache,
                self.__fast_period,
                self.__slow_period
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class bop:
    """能量均衡指标"""

    def __init__(
        self, 
        init_count: int, 
        fast_period: int,
        slow_period: int,
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"

        # 初始计数
        self.__init_count = init_count
        self.__fast_period = fast_period
        self.__slow_period = slow_period

        # 价格序列缓存
        self.__open_cache: np.ndarray = np.zeros(init_count)
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, open: float, close: float, high: float, low: float) -> float:
        """添加新的价格数据"""

        # 添加数据
        self.__open_cache[:-1] = self.__open_cache[1:]
        self.__open_cache[-1] = open
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            result = talib.BOP(
                self.__open_cache,
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(result[-1])

            return result[-1]
        return None


class stoch:
    """随机指数，kdj中的kd"""

    def __init__(
        self, 
        init_count: int, 
        fastk_period: int,
        slowk_period: int,
        slowk_matype: int,
        slowd_period: int,
        slowd_matype: int,
        call_back=None
    ):
        """初始化"""

        assert init_count > 1, f"初始化计数init_count必须大于1"

        # 初始计数
        self.__init_count = init_count
        self.__fastk_period = fastk_period
        self.__slowk_period = slowk_period
        self.__slowk_matype = slowk_matype
        self.__slowd_period = slowd_period
        self.__slowd_matype = slowd_matype

        # 价格序列缓存
        self.__close_cache: np.ndarray = np.zeros(init_count)
        self.__high_cache: np.ndarray = np.zeros(init_count)
        self.__low_cache: np.ndarray = np.zeros(init_count)

        # 回调对象
        self.__call_back = call_back

    def append_data(self, open: float, close: float, high: float, low: float) -> (float, float):
        """添加新的价格数据"""

        # 添加数据
        self.__close_cache[:-1] = self.__close_cache[1:]
        self.__close_cache[-1] = close
        self.__high_cache[:-1] = self.__high_cache[1:]
        self.__high_cache[-1] = high
        self.__low_cache[:-1] = self.__low_cache[1:]
        self.__low_cache[-1] = low

        # 判断是否触发计算
        if len(self.__price_cache) >= self.__init_count:
            k, d = talib.STOCH(
                self.__high_cache, 
                self.__low_cache, 
                self.__close_cache,
                self.__fastk_period,
                self.__slowk_period,
                self.__slowk_matype,
                self.__slowd_period,
                self.__slowd_matype
            )

            # 触发回调
            if self.__call_back is not None:
                self.__call_back(k[-1], d[-1])

            return k[-1], d[-1]
        return None

