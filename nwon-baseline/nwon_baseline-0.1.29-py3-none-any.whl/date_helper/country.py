from datetime import datetime
from typing import Optional

import pytz


def timezone_offset_from_country_code(country_code: str) -> Optional[float]:
    timezones = timezones_from_country_code(country_code)

    if timezones is None:
        return None

    timezone_to_use = pytz.timezone(timezones[0])
    timezone_offset = datetime.now(timezone_to_use).utcoffset()
    return timezone_offset.total_seconds() if timezone_offset else None


def timezones_from_country_code(country_code: str) -> Optional[list[str]]:
    if country_code not in pytz.country_timezones:
        return None

    return pytz.country_timezones[country_code]


__all__ = ["timezone_offset_from_country_code", "timezones_from_country_code"]
