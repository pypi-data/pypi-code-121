import pytz
import logging
from datetime import datetime, timedelta, tzinfo
from tzlocal import get_localzone
from typing import Union, NamedTuple, Tuple, Optional, Any
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from ..error.utils import InputDataError

DATETIME_FMT_FULL = "%Y-%m-%d %H:%M:%S"
DATETIME_FMT_DATE = "%Y-%m-%d"
DATETIME_FMT_TIME = "%H:%M:%S"
# many systems (e.g. Mongo) does not support default datetime.min (0001-01-01 00:00:00),
# so we have to use a conservative value as minimal datetime.
DATETIME_SAFE_MIN = datetime(1900, 1, 1)


class TimeWindow(NamedTuple):
    start: datetime
    end: datetime


def time_slice(start_1: datetime, end_1: datetime, start_2: datetime,
               end_2: datetime, delta: timedelta) -> \
        Tuple[Optional[TimeWindow], Optional[TimeWindow], Optional[TimeWindow]]:
    """
    Let tw_1 = TimeWindow(start_1, end_1)
    Let tw_2 = TimeWindow(start_2, end_2)
    Use tw_2 to slice tw_1 into at most 3 pieces:
        * piece before tw_2
        * piece inside tw_2
        * piece after tw_2
    """
    max_start = max(start_1, start_2)
    min_end = min(end_1, end_2)
    tw_before_2 = None
    tw_inside_2 = None
    tw_after_2 = None
    if start_1 < start_2:
        # Cases that tw_before_2 exist
        # 1: [ ]     | [   ]   | [     ]
        # 2:     [ ] |   [   ] |   [ ]
        end_before_2 = min(start_2 - delta, end_1)
        tw_before_2 = TimeWindow(start_1, end_before_2)
    if max_start <= min_end:
        # Cases that tw_inside_2 exist
        # 1: [   ]   | [     ] |   [   ] |   [ ]
        # 2:   [   ] |   [ ]   | [   ]   | [     ]
        tw_inside_2 = TimeWindow(max_start, min_end)
    if end_1 > end_2:
        # Cases that tw_after_2 exist
        # 1: [     ] |   [   ] |     [ ]
        # 2:   [ ]   | [   ]   | [ ]
        start_after_2 = max(end_2 + delta, start_1)
        tw_after_2 = TimeWindow(start_after_2, end_1)
    return tw_before_2, tw_inside_2, tw_after_2


def parse_delta(s: str, raise_on_error: bool = True):
    err_msg = f"Invalid delta str '{s}'"
    try:
        if not s:
            raise ValueError(err_msg)
        if len(s) < 2:
            raise ValueError(err_msg)
        amount = int(s[:-1])
        unit = s[-1]
        if unit == 'y':
            return relativedelta(years=amount)
        if unit == 'M':
            return relativedelta(months=amount)
        if unit == 'w':
            return relativedelta(weeks=amount)
        if unit == 'd':
            return relativedelta(days=amount)
        if unit == 'h':
            return relativedelta(hours=amount)
        if unit == 'm':
            return relativedelta(minutes=amount)
        if unit == 's':
            return relativedelta(seconds=amount)
        raise ValueError(err_msg)
    except ValueError:
        if raise_on_error:
            raise
        else:
            return None


def parse_time(s: str):
    return parse(s)


def get_datetime(time_zone: Optional[str]=None) -> datetime:
    return datetime.now() if time_zone is None or len(time_zone) == '' else datetime.now(pytz.timezone(time_zone))


def get_datetime_str(time_zone: Optional[str]=None) -> str:
    return datetime.now() if time_zone is None or len(time_zone) == '' else datetime.now(pytz.timezone(time_zone)).strftime(DATETIME_FMT_FULL)


def get_date(time_zone: Optional[str]=None) -> str:
    return get_datetime(time_zone).strftime(DATETIME_FMT_DATE)


def get_datetime_stamp(time_zone: Optional[str]=None) -> float:
    return get_datetime(time_zone).timestamp()


def get_datetime_from_stamp(timestamp, time_zone: Optional[str]=None):
    return datetime.fromtimestamp(timestamp) if time_zone is None else datetime.fromtimestamp(timestamp, pytz.timezone(time_zone))


def get_timezone(tz_name: str, fallback_tz_name: Optional[str] = None) -> Tuple[Any, str]:
    final_tz_name = None
    tz = None
    try:
        tz = pytz.timezone(tz_name)
        final_tz_name = tz_name
    except pytz.exceptions.UnknownTimeZoneError:
        logging.error(f"Unknown timezone {tz_name}! Fallback to {fallback_tz_name}.")

    if not tz:
        if fallback_tz_name:
            try:
                tz = pytz.timezone(fallback_tz_name)
                final_tz_name = fallback_tz_name
            except pytz.exceptions.UnknownTimeZoneError:
                logging.error(f"Unknown fallback timezone {fallback_tz_name}!")
    if not tz:
        raise InputDataError(
            f'Unknown timezone {tz_name} and fallback timezone {fallback_tz_name}'
        )

    return tz, final_tz_name


def convert_str_to_datetime(time: str, fmt: str, time_zone: Optional[str] = None):
    time = datetime.strptime(time, fmt)
    if time_zone is not None:
        time = time.replace(tzinfo=get_timezone(str(time_zone))[0])
    return time


def convert_time_with_timezone(time: datetime, target_tz: str):
    target_tz = get_timezone(str(target_tz))[0]
    return time.replace(tzinfo=target_tz)


def convert_time_by_timezone(original_time: datetime,
                           original_tz: Union[str, tzinfo],
                           target_tz: Union[str, tzinfo]) -> datetime:
    if not isinstance(original_time, datetime):
        raise InputDataError(f"orignial_time must be datetime object!")
    if not original_tz:
        raise InputDataError(f"original_tz cannot be None.")
    if not target_tz:
        raise InputDataError(f"target_tz cannot be None.")
    if not isinstance(original_tz, tzinfo):
        original_tz = get_timezone(str(original_tz))[0]
    if not isinstance(target_tz, tzinfo):
        target_tz = get_timezone(str(target_tz))[0]
    converted_time = original_tz.localize(original_time).astimezone(target_tz).replace(tzinfo=None)
    return converted_time


def convert_stamp(stamp: int, original_tz: Union[str, tzinfo], target_tz: Union[str, tzinfo]) -> datetime:
    if not isinstance(stamp, int):
        raise InputDataError(f"stamp must be int object!")
    if not original_tz:
        raise InputDataError(f"original_tz cannot be None.")
    if not target_tz:
        raise InputDataError(f"target_tz cannot be None.")
    if not isinstance(original_tz, tzinfo):
        original_tz = get_timezone(str(original_tz))[0]
    if not isinstance(target_tz, tzinfo):
        target_tz = get_timezone(str(target_tz))[0]

    return convert_time_by_timezone(get_datetime_from_stamp(stamp), original_tz, target_tz)

def convert_time(time: Union[int, str, datetime], original_tz: Union[str, tzinfo, None], target_tz: Union[str, tzinfo, None]) -> datetime:
    if isinstance(time, str):
        time = parse_time(time)
    elif isinstance(time, int):
        if isinstance(original_tz, str):
            time = get_datetime_from_stamp(time, original_tz)
        elif isinstance(original_tz, tzinfo):
            time = get_datetime_from_stamp(time, original_tz.zone)
        else:
            time = get_datetime_from_stamp(time)
    if original_tz and not isinstance(original_tz, tzinfo):
        original_tz = get_timezone(str(original_tz))[0]
    if target_tz and not isinstance(target_tz, tzinfo):
        target_tz = get_timezone(str(target_tz))[0]
    if not time.tzinfo and isinstance(original_tz, tzinfo):
        time = original_tz.localize(time)
    if isinstance(target_tz, tzinfo):
        time = time.astimezone(target_tz)
    return time.replace(tzinfo=None)
