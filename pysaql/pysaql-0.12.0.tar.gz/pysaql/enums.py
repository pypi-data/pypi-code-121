"""Contains enum definitions"""

from enum import Enum


class StrEnum(Enum):
    """Base class for an enum that renders its value as string"""

    def __str__(self) -> str:
        """Cast enum to a string"""
        return str(self.value)


class Order(StrEnum):
    """Sort order"""

    asc = "asc"
    desc = "desc"


class JoinType(StrEnum):
    """Join/cogroup type"""

    inner = "inner"
    left = "left"
    right = "right"
    full = "full"


class DateDiffUnit(StrEnum):
    """Unit for calculating the difference between datetimes"""

    year = "year"
    quarter = "quarter"
    month = "month"
    day = "day"
    week = "week"
    hour = "hour"
    minute = "minute"
    second = "second"


class RelativeTimeframe(StrEnum):
    """Timeframe for defining a relative date"""

    current = "current"
    future = "ahead"
    past = "ago"


class RelativeDateUnit(StrEnum):
    """Unit for defining a relative date"""

    year = "year"
    quarter = "quarter"
    month = "month"
    day = "day"
    week = "week"
    fiscal_year = "fiscal_year"
    fiscal_quarter = "fiscal_quarter"


class FillDateTypeString(StrEnum):
    """Date format string used to fill time series"""

    y_m = "Y-M"
    y_q = "Y-Q"
    y = "Y"
    y_w = "Y-W"
    y_m_d = "Y-M-D"
