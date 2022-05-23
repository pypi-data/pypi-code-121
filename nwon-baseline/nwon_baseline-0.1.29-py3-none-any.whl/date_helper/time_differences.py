from datetime import datetime, timedelta
from typing import Tuple

from nwon_baseline.date_helper.datetime import datetime_now


def time_until(date_time: datetime) -> Tuple[int, int, int]:
    """
    Time from now until a given date_time.

    Returned is a Tuple of (days, hours, minutes)
    """

    time_since: timedelta = date_time - datetime_now()
    hours = time_since.seconds // 3600
    minutes = (time_since.seconds // 60) % 60

    return (time_since.days, hours, minutes)


__all__ = ["time_until"]
