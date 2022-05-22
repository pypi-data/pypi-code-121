import abc
import asyncio
import functools
import itertools
import logging
import time
from typing import (
    AsyncGenerator,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    SupportsFloat,
    TypeVar,
    Union,
)

from classiq.exceptions import ClassiqValueError

T = TypeVar("T")
ASYNC_SUFFIX = "_async"

_logger = logging.getLogger(__name__)


def get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        _logger.info("Creating an event loop, since none exists", exc_info=True)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def run(coro: Awaitable[T]) -> T:
    # Use this function instead of asyncio.run, since it ALWAYS
    # creates a new event loop and clears the thread event loop.
    # Never use asyncio.run in library code.
    loop = get_event_loop()
    return loop.run_until_complete(coro)


def syncify_function(async_func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    @functools.wraps(async_func)
    def async_wrapper(*args, **kwargs) -> T:
        return run(async_func(*args, **kwargs))

    # patch `functools.wraps` work on `name` and `qualname`
    for attr in ("__name__", "__qualname__"):
        name = getattr(async_wrapper, attr, "")
        if name.endswith(ASYNC_SUFFIX):
            setattr(async_wrapper, attr, name[: -len(ASYNC_SUFFIX)])

    return async_wrapper


# Explanation about metaclasses
# https://stackoverflow.com/questions/100003/what-are-metaclasses-in-python


class Asyncify(type):
    def __new__(mcls, name: str, bases: tuple, class_dict: dict):
        new_attrs = {}

        for attr_name, attr_value in class_dict.items():
            if attr_name.endswith(ASYNC_SUFFIX):
                new_attr_name = attr_name[: -len(ASYNC_SUFFIX)]
                if new_attr_name in class_dict:
                    raise ClassiqValueError(f"Method name collision: {attr_name}")
                else:
                    new_attrs[new_attr_name] = attr_value

        new_class = super().__new__(mcls, name, bases, class_dict)

        for attr_name, attr_value in new_attrs.items():
            setattr(new_class, attr_name, syncify_function(attr_value))

        return new_class


# Used for resolving metaclass collision
class AsyncifyABC(Asyncify, abc.ABCMeta):
    pass


def enable_jupyter_notebook() -> None:
    import nest_asyncio  # type: ignore[import]

    nest_asyncio.apply()


def _make_iterable_interval(
    interval_sec: Union[SupportsFloat, Iterable[SupportsFloat]]
) -> Iterable[float]:
    if isinstance(interval_sec, Iterable):
        return map(float, interval_sec)
    return itertools.repeat(float(interval_sec))


async def poll_for(
    poller: Callable[..., Awaitable[T]],
    timeout_sec: Optional[float],
    interval_sec: Union[float, Iterable[float]],
) -> AsyncGenerator[T, None]:
    if timeout_sec is not None:
        end_time = time.perf_counter() + timeout_sec
    else:
        end_time = None
    interval_sec_it = iter(_make_iterable_interval(interval_sec))
    while end_time is None or time.perf_counter() < end_time:
        yield await poller()
        cur_interval_sec = next(interval_sec_it)
        if cur_interval_sec:
            await asyncio.sleep(cur_interval_sec)


# =======================================================================
# According to stackoverflow.com's license
# taken from:
#   https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
# from the user:
#   https://stackoverflow.com/users/2132753/gustavo-bezerra
def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined]
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


# =======================================================================
