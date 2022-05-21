import locale
import threading

from datetime import datetime, timedelta, timezone
from contextlib import contextmanager, nullcontext
from typing import Optional

import babel.dates
from babel.dates import format_datetime

# constants
DAYS_IN_YEAR = 365.6
DAYS_IN_MONTH = DAYS_IN_YEAR / 12
DAYS_IN_WEEK = 7
HOURS_IN_DAY = 24
MINS_IN_HOUR = 60
SECS_IN_MIN = 60
SECS_IN_HOUR = SECS_IN_MIN * MINS_IN_HOUR
SECS_IN_DAY = SECS_IN_HOUR * HOURS_IN_DAY
SECS_IN_WEEK = SECS_IN_DAY * DAYS_IN_WEEK
SESC_IN_MONTH = SECS_IN_DAY * DAYS_IN_MONTH
SECS_IN_YEAR = SECS_IN_DAY * DAYS_IN_YEAR


LDML_TO_POSIX = {
    "y": "%y",
    "Y": "%Y",
    "M": "%b",
    "w": "%W",
    "D": "%j",
    "d": "%d",
    "F": "%w",
    "E": "%A",
    "a": "%p",
    "H": "%H",
    "K": "%I",
    "m": "%M",
    "s": "%S",
    "z": "%Z",
    "Z": "%z",
}
"""Approximate mapping from LDML (Simple Java Date Format) to POSIX format."""


LOCALE_LOCK = threading.Lock()
"""lock to be able to use strftime in multi-threaded python"""


@contextmanager
def setlocale(name):
    """
    Set locale for str{p,f}time.

    Python's setlocale is not thread-safe, this creates thread-safe
    implementation by using a mutex

    Adapted from https://stackoverflow.com/a/24070673
    """
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_TIME)
        try:
            yield locale.setlocale(locale.LC_TIME, name)
        finally:
            locale.setlocale(locale.LC_TIME, saved)


def read_cformat(input_: str, cformat: str) -> Optional[datetime]:
    """Try to parse POSIX-formatted date & time."""
    try:
        return datetime.strptime(input_.strip(), cformat)
    except ValueError:
        return None


def read_jformat(input_: str, jformat: str) -> Optional[datetime]:
    """
    Try to parse j-formatted date & time.

    As currently there is no Python library that supports parsing j-format
    fully, we will only approximate by POSIX format.
    """
    format_ = jformat
    for k, v in LDML_TO_POSIX.items():
        format_ = format_.replace(k, v)
    return read_cformat(input_, format_)


def extract_diff(diff: timedelta, type_: str) -> Optional[str]:
    """Try to extract specified time unit from datetime."""
    secs = diff.total_seconds()
    if type_ == "minutes":
        return f"{secs // SECS_IN_MIN:.0f}"
    elif type_ == "hours":
        return f"{secs // SECS_IN_HOUR:.0f}"
    elif type_ == "days":
        return f"{secs // SECS_IN_DAY:.0f}"
    elif type_ == "weeks":
        return f"{secs // SECS_IN_WEEK:.0f}"
    elif type_ == "months":
        return f"{secs // SESC_IN_MONTH:.0f}"
    elif type_ == "years":
        return f"{secs // SECS_IN_YEAR:.0f}"
    return None


def format_now(locale_: Optional[str], timezone_: Optional[str],
               cformat: Optional[str], jformat: Optional[str])\
        -> Optional[str]:
    """
    Format current date-time.

    Implements AIML <date/> tag with various formats it allows. Only
    current time (now()) is fetched, formatted and returned.

    Exactly one of `cformat` and `jformat` must be specified.

    :param locale_: locale to which we fetch current time
    :param timezone_: timezone offset to get current time, represents int
        offset in hours
    :param cformat: POSIX date-time format (see `man strftime`)
    :param jformat: format based on Java-Simple-Date format specs.
    :return: formatted date or None if locale_ or time do not have the correct
        form
    """
    if timezone_ is None:
        timezone_ = "0"
    if not timezone_.isdecimal():
        return None
    if not cformat and not jformat:
        raise ValueError("one of cformat and jformat must be specified.")

    tz = int(timezone_)
    now = datetime.now(tz=timezone(timedelta(hours=tz)))

    if cformat is not None:
        ct = nullcontext() if locale_ is None else setlocale(locale_)
        with ct:
            return now.strftime(cformat)

    else:
        if locale_ is None:
            locale_ = babel.dates.LC_TIME
        res: str = format_datetime(now, jformat, locale=locale_)
        return res
