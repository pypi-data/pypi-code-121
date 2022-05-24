# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import traceback

from contextlib import contextmanager

from .base import Utils


# 基础异常
class BaseError(Exception):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


class Ignore(BaseError):
    """可忽略的异常

    用于with语句块跳出，或者需要跳出多层逻辑的情况

    """

    def __init__(self, *args, layers=1, **kwargs):

        super().__init__(*args, **kwargs)

        self._layers = layers

        if err := str(self):
            Utils.log.warning(err)

    def throw(self):

        if self._layers > 0:
            self._layers -= 1

        return self._layers != 0


@contextmanager
def catch_warning(intercept=False):
    """异常捕获，打印warning级日志

    通过with语句捕获异常，代码更清晰，还可以使用Ignore异常安全的跳出with代码块

    """

    try:

        yield

    except Ignore as err:

        if intercept is True:
            Utils.log.warning(traceback.format_exc())
        elif err.throw():
            raise err

    except:

        Utils.log.warning(traceback.format_exc())


@contextmanager
def catch_error(intercept=False):
    """异常捕获，打印error级日志

    通过with语句捕获异常，代码更清晰，还可以使用Ignore异常安全的跳出with代码块

    """

    try:

        yield

    except Ignore as err:

        if intercept is True:
            Utils.log.error(traceback.format_exc())
        elif err.throw():
            raise err

    except:

        Utils.log.error(traceback.format_exc())


@contextmanager
def take_time(log_str):
    """耗时统计

    """

    _time = time.time() * 1000

    try:
        yield
    except Exception as err:
        raise err
    finally:
        Utils.log.debug(f'{log_str} ==> {time.time() * 1000 - _time}ms')


# 数据库只读限制异常
class MySQLReadOnlyError(BaseError):
    pass


# 数据库客户端已销毁
class MySQLClientDestroyed(BaseError):
    pass


# NTP校准异常
class NTPCalibrateError(BaseError):
    pass
