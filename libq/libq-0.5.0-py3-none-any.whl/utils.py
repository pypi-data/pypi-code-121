import asyncio
import calendar
import numbers
from datetime import datetime
from importlib import import_module
from typing import AsyncGenerator, Callable, Union

from nanoid import generate

from libq.errors import TimeoutFormatError


def generate_random(size=10):

    return generate(size=size)


def now_secs() -> float:
    """ gives the utc now times in timestamp format """
    return datetime.utcnow().timestamp()


def now_iso() -> str:
    """ gives the utc now times in isoformat format """
    return datetime.utcnow().isoformat()


def now_dt() -> datetime:
    return datetime.utcnow()


def elapsed_from(dt: Union[str, float], *, now=None) -> float:
    """ measure the difference from a isoformat date or a timestamp """
    now = now or now_secs()
    if isinstance(dt, str):
        _dt = datetime.fromisoformat(dt).timestamp()
    elif isinstance(dt, float):
        _dt = dt
    else:
        raise TypeError("Invalid date format nor iso nor timestamp")
    return now - _dt


def from_unix(string) -> datetime:
    """Convert a unix timestamp into a utc datetime"""
    return datetime.utcfromtimestamp(float(string))


def to_unix(dt: datetime):
    """Converts a datetime object to unixtime"""
    return calendar.timegm(dt.utctimetuple())


def parse_timeout(timeout) -> Union[int, None]:
    """Transfer all kinds of timeout format to an integer representing seconds"""
    if not isinstance(timeout, numbers.Integral) and timeout is not None:
        try:
            timeout = int(timeout)
        except ValueError:
            digit, unit = timeout[:-1], (timeout[-1:]).lower()
            unit_second = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
            try:
                timeout = int(digit) * unit_second[unit]
            except (ValueError, KeyError):
                raise TimeoutFormatError('Timeout must be an integer or a string representing an integer, or '
                                         'a string with format: digits + unit, unit can be "d", "h", "m", "s", '
                                         'such as "1h", "23m".')

    return timeout


async def poll(step: float = 0.5) -> AsyncGenerator[float, None]:
    loop = asyncio.get_event_loop()
    start = loop.time()
    while True:
        before = loop.time()
        yield before - start
        after = loop.time()
        wait = max([0, step - after + before])
        await asyncio.sleep(wait)


def get_function(fullname) -> Callable:
    mod, name = fullname.rsplit(".", maxsplit=1)
    pkg = mod.split(".", maxsplit=1)[0]
    try:
        module = import_module(mod, pkg)
    except (ModuleNotFoundError, AttributeError):
        raise KeyError(fullname)
    return getattr(module, name)
