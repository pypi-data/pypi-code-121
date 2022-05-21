import datetime as dt
from typing import Any
from typing import Optional

from pandas import NaT
from pandas import Timestamp


Int64 = "Int64"
boolean = "boolean"
string = "string"


def timestamp_to_date(timestamp: Any, /) -> Optional[dt.date]:
    """Convert a timestamp to a date."""

    if (value := timestamp_to_datetime(timestamp)) is None:
        return None
    else:
        return value.date()


def timestamp_to_datetime(timestamp: Any, /) -> Optional[dt.datetime]:
    """Convert a timestamp to a datetime."""

    if isinstance(timestamp, Timestamp):
        return timestamp.to_pydatetime()
    elif timestamp is NaT:
        return None
    else:
        raise TypeError(f"Invalid type: {type(timestamp).__name__!r}")
