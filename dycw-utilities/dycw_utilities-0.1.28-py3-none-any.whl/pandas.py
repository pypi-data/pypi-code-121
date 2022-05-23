import datetime as dt
from typing import Any
from typing import cast

from pandas import NaT
from pandas import Timestamp


TIMESTAMP_MIN = cast(Timestamp, Timestamp.min)
TIMESTAMP_MAX = cast(Timestamp, Timestamp.max)
Int64 = "Int64"
boolean = "boolean"
string = "string"


def timestamp_to_date(timestamp: Any, /) -> dt.date:
    """Convert a timestamp to a date."""

    return timestamp_to_datetime(timestamp).date()


def timestamp_to_datetime(timestamp: Any, /) -> dt.datetime:
    """Convert a timestamp to a datetime."""

    if timestamp is NaT:
        raise ValueError(f"Invalid value: {timestamp}")
    else:
        return timestamp.to_pydatetime()


def _timestamp_minmax_to_date(
    timestamp: Timestamp, method_name: str, /
) -> dt.date:
    """Get the maximum Timestamp as a date."""

    method = getattr(timestamp, method_name)
    rounded = cast(Timestamp, method("D"))
    return timestamp_to_date(rounded)


TIMESTAMP_MIN_AS_DATE = _timestamp_minmax_to_date(TIMESTAMP_MIN, "ceil")
TIMESTAMP_MAX_AS_DATE = _timestamp_minmax_to_date(TIMESTAMP_MAX, "floor")


def _timestamp_minmax_to_datetime(
    timestamp: Timestamp, method_name: str, /
) -> dt.datetime:
    """Get the maximum Timestamp as a datetime."""

    method = getattr(timestamp, method_name)
    rounded = cast(Timestamp, method("us"))
    return timestamp_to_datetime(rounded)


TIMESTAMP_MIN_AS_DATETIME = _timestamp_minmax_to_datetime(TIMESTAMP_MIN, "ceil")
TIMESTAMP_MAX_AS_DATETIME = _timestamp_minmax_to_datetime(
    TIMESTAMP_MAX, "floor"
)
