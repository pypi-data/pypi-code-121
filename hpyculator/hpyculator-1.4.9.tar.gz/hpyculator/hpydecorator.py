from typing import Callable, Tuple
import time


def reRunTimes(times: int = 1) -> Callable:
    """
    一个装饰器，用来计算函数运行时长，这个函数是装饰器参数

    :param times: 运行次数，默认为1
    :return: 一个元组，第一项为函数的返回值，第二项为函数运行时长
    """

    def ruturnFun(fun: Callable) -> Callable:
        """
        装饰器本体

        :param fun: 要装饰的函数
        :return: 函数
        """

        def runFun(*args, **kwargs) -> Tuple[Callable, float]:
            """
            装饰器

            :param args: 参
            :param kwargs: 形参
            :return: 函数
            """
            _time_start = time.perf_counter()
            for _ in range(times):
                fun_ret = fun(*args, **kwargs)
            time_used = time.perf_counter() - _time_start
            return fun_ret, time_used

        return runFun

    return ruturnFun


def funName(fun: Callable) -> Callable:
    """
    一个装饰器，函数形参增加__name__用于获得函数名

    :param fun: 一个函数
    :return: 一个函数
    """
    name = fun.__name__

    def ret_fun(*args, **kwargs) -> Callable:
        """
        装饰器

        :param args: 参
        :param kwargs: 形参
        :return: 函数
        """
        return fun(*args, __fun_name__=name, **kwargs)

    return ret_fun
