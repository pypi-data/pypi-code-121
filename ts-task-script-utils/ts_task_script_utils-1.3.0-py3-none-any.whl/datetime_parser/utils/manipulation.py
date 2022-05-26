import datetime as dt
import re
from itertools import product
from typing import Mapping, Optional, Sequence, Tuple

from pendulum import now
from pendulum.tz import timezone as pendulum_timezone
from pendulum import datetime as pendulum_datetime
from pydash.arrays import flatten
from task_script_utils.datetime_parser.fractional_seconds_formatter import (
    FractionalSecondsFormatter,
)
from task_script_utils.datetime_parser.ts_datetime import TSDatetime

_formatter = FractionalSecondsFormatter()

TIME_PARTS = [
    ["h", "hh", "H", "HH"],
    ["m", "mm"],
    ["s", "ss"],
]


def map_offset_to_seconds(tz_dict):
    """
    Convert dict that maps from abbreviated_tz -> utc_offset
    to a dict that maps abbreviated_tz -> total_seconds
    eg. {"ist": "+05:30"} ---> {"ist": 19800.0}
    """
    return {
        tz.upper(): convert_offset_to_seconds(utc_offset)
        for tz, utc_offset in tz_dict.items()
    }


def get_time_formats_for_long_date(fractional_seconds: Optional[str]) -> Tuple:
    def map_am_pm(time_format):
        return time_format if time_format.startswith("H") else time_format + " A"

    time_formats = [":".join(tokens) for tokens in product(*TIME_PARTS)]
    if fractional_seconds:
        token = "SSSSSS"
        time_formats = map(lambda x: [x, f"{x}.{token}"], time_formats)

    time_formats = flatten(time_formats)
    time_formats = map(lambda x: map_am_pm(x), time_formats)
    time_formats = map(
        lambda x: [x, x + " Z", x + " z", x + " ZZ", x + " Z z", x + " ZZ z"],
        time_formats,
    )
    time_formats = flatten(time_formats)
    return tuple(time_formats)


def convert_offset_to_seconds(offset_value: str):
    """Convert +/-hh:mm utc offset string value
    to +/-<seconds>
    eg. +00:33 --> 1980.0
    eg. -00:33 --> -1980.0
    """
    sign, offset = offset_value[0], offset_value[1:]
    sign = -1 if sign == "-" else 1
    hrs, mins = offset.split(":")
    total_seconds = dt.timedelta(hours=int(hrs), minutes=int(mins)).total_seconds()
    return sign * total_seconds


def replace_abbreviated_tz_with_utc_offset(
    datetime_str: str, tz_dict: Optional[Mapping] = None
):
    """
    Converts `12-12-2012 12:12:12 AM IST` to `12-12-2012 12:12:12 AM +05:30`
    if `IST: +05:30` exist in tz_dict
    """
    for tz_name in tz_dict:
        if tz_name in datetime_str:
            return datetime_str.replace(tz_name, tz_dict[tz_name])
    return datetime_str


def replace_zz_with_Z(formats: Sequence[str] = ()):
    """
    eg. `DD-MM-YYYY hh:m:ss zz` -> `DD-MM-YYYY hh:m:ss Z`
    """
    result_formats = list(formats)
    for idx, format_ in enumerate(result_formats):
        if "zz" in format_:
            result_formats[idx] = format_.replace("zz", "Z")

    return result_formats


def from_pendulum_format(
    datetime_string: str,
    fmt: str,
    tz: Optional[pendulum_timezone] = None,
    locale=None,
) -> TSDatetime:
    """
    Creates a DateTime instance from a specific format.
    """
    subseconds = None
    parts = _formatter.parse(datetime_string, fmt, now(), locale=locale)
    if not isinstance(parts, dict):
        raise TypeError(f"Could not match any datetime tokens in '{fmt}'.")
    if parts["tz"] is None:
        parts["tz"] = tz

    if "S" in fmt:
        subseconds = parts["microsecond"]
        parts["microsecond"] = 0

    ts_date_time = TSDatetime(
        datetime_=pendulum_datetime(**parts), subseconds=subseconds
    )
    return ts_date_time


def replace_z_with_offset(datetime_str: str) -> str:
    """
    12-12-12T14:53:00Z -> 12-12-12T14:53:00+00:00
    12-12-12T14:53:00 Z -> 12-12-12T14:53:00 +00:00
    """
    return re.sub(r"(?<=\d|\s)Z(?=\s|$)", "+00:00", datetime_str)
