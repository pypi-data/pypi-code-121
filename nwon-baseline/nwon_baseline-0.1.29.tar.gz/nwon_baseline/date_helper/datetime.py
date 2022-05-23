from datetime import datetime

import pytz


def datetime_now() -> datetime:
    """
    Returns the timezone aware current date time.
    """

    return pytz.utc.localize(datetime.now())


def datetime_with_timezone(datetime_to_use: datetime) -> datetime:
    """
    Attaches timezone information to datetime if none is already included
    """

    return (
        datetime_to_use
        if datetime_to_use.tzinfo
        else pytz.utc.localize(datetime_to_use)
    )


__all__ = ["datetime_now", "datetime_with_timezone"]
