import time
import traceback
from functools import wraps

from .constants import LOG_PREFIX
from .log_utils import get_fmpc_logger

logger = get_fmpc_logger(__name__)


def exec_time(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        st = time.time()
        result = func(*args, **kwargs)
        logger.info(f"{LOG_PREFIX}方法 {func.__name__} 执行时间，{(time.time()-st):.5f}s")
        return result
    return wrap


def exec_log(mess):
    def decorator(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            st = time.time()
            log = kwargs.get("log")
            if log:
                log(f"{LOG_PREFIX}{mess}开始")
            result = func(*args, **kwargs)
            if log:
                log(f"{LOG_PREFIX}{mess}结束")
            logger.info(f"{LOG_PREFIX}方法 {func.__name__} 执行时间，{(time.time()-st):.5f}s")
            return result
        return wrap
    return decorator


def exec_except(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as ex:
            logger.info(traceback.format_exc())
            raise RuntimeError(f"{LOG_PREFIX}方法 {func.__name__} 运行异常，{repr(ex)}")
        return result
    return wrap
