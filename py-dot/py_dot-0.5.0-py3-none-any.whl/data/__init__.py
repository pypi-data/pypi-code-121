from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Type, Union, List, Tuple, Dict, TypedDict, Optional, TypeVar

from py_dot.core.date import Period, DateParts
from py_dot.data.summary_time_unit import SummaryTimeUnit


class SummaryTimeUnits:
    year = 'year'
    month = 'month'
    date = 'date'
    hour = 'hour'
    minute = 'minute'
    second = 'second'

    def __init__(
            self,
            year=None,
            month=None,
            date=None,
            hour=None,
            minute=None,
            second=None,
            default=None
    ):
        if year is None and month is None and date is None and hour is None and minute is None and second:
            if default is None:
                raise ValueError('One of time value is required at least.')

        self.year = year
        self.month = month
        self.date = date
        self.hour = hour
        self.minute = minute
        self.second = second
        self.default = default


class SummaryCondition:
    def __init__(
            self,
            units: Union[SummaryTimeUnits, Type[SummaryTimeUnits]] = SummaryTimeUnit,
            year_days: int = 365,
            month_days: int = 30,
            year_from: int = 3,
            month_from: int = 6,
            date_from: int = 7,
            hour_from: int = 28,
            minute_from: int = 3599
    ):
        self.units = units
        self.year_days = year_days
        self.month_days = month_days
        self.year_from = year_from
        self.month_from = month_from
        self.date_from = date_from
        self.hour_from = hour_from
        self.minute_from = minute_from

    def auto(self, period: Period):
        duration_time = period.duration_time
        days = ceil(duration_time / 86400)

        units = self.units

        if units.year is not None:
            if days >= self.year_days * self.year_from:
                return self.year(period)

        if units.month is not None:
            if units.date is None or days >= self.month_days * self.month_from:
                return self.month(period)

        if units.date is not None:
            if units.hour is None or days >= self.date_from:
                return self.day(period)

        if units.hour is not None:
            if units.minute is None or days >= self.hour_from:
                return self.hour(period)

        if units.minute is not None:
            if duration_time >= self.minute_from:
                return self.minute(period)

        return self.second(period)

    def year(self, period: Period):
        return (
            SummaryTimeUnit.year,
            self.units.year,
            DataSummaryTime(period.begin).y,
            DataSummaryTime(period.end).y
        )

    def month(self, period: Period):
        return (
            SummaryTimeUnit.month,
            self.units.month,
            DataSummaryTime(period.begin).ym,
            DataSummaryTime(period.end).ym
        )

    def day(self, period: Period):
        return (
            SummaryTimeUnit.date,
            self.units.date,
            DataSummaryTime(period.begin).ymd,
            DataSummaryTime(period.end).ymd
        )

    def hour(self, period: Period):
        return (
            SummaryTimeUnit.hour,
            self.units.hour,
            DataSummaryTime(period.begin).ymdh,
            DataSummaryTime(period.end).ymdh
        )

    def minute(self, period: Period):
        return (
            SummaryTimeUnit.minute,
            self.units.minute,
            DataSummaryTime(period.begin).ymdhi,
            DataSummaryTime(period.end).ymdhi
        )

    def second(self, period: Period):
        return (
            SummaryTimeUnit.second,
            self.units.second,
            DataSummaryTime(period.begin).ymdhis,
            DataSummaryTime(period.end).ymdhis
        )

    def get(self, period: Period, unit: SummaryTimeUnit):
        return self.__getattribute__(unit.value)(period)


class DataSummaryTime:
    def __init__(self, time: datetime = None, parts: DateParts = None):
        if parts is None:
            if time is None:
                raise ValueError('time or parts Arguments is Required.')

            parts = DateParts(time)

        y, m, d, h, i, s = parts

        ym = y + m
        ymd = ym + d
        ymdh = ymd + h
        ymdhi = ymdh + i
        ymdhis = ymdhi + s

        self.y = time.replace(year=int(y), month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        self.ym = self.y.replace(month=int(m))
        self.ymd = self.ym.replace(day=int(d))
        self.ymdh = self.ymd.replace(hour=int(h))
        self.ymdhi = self.ymdh.replace(minute=int(m))
        self.ymdhis = self.ymdhi.replace(second=int(s))


class DataSummaryTimeDigits:
    def __init__(self, time: datetime = None, parts: DateParts = None):
        if parts is None:
            if time is None:
                raise ValueError('time or parts Arguments is Required.')

            parts = DateParts(time)

        y, m, d, h, i, s = parts

        ym = y + m
        ymd = ym + d
        ymdh = ymd + h
        ymdhi = ymdh + i
        ymdhis = ymdhi + s

        self.y = int(y)
        self.ym = int(ym)
        self.ymd = int(ymd)
        self.ymdh = int(ymdh)
        self.ymdhi = int(ymdhi)
        self.ymdhis = int(ymdhis)


@dataclass
class DataSummaryTimeStrings:
    def __init__(self, time: datetime = None, parts: DateParts = None):
        if parts is None:
            if time is None:
                raise ValueError('time or parts Arguments is Required.')

            parts = DateParts(time)

        y, m, d, h, i, s = parts

        ym = y + '-' + m
        ymd = ym + '-' + d
        ymdh = ymd + ' ' + h
        ymdhi = ymdh + ':' + i
        ymdhis = ymdhi + ':' + s

        self.y = y
        self.ym = ym
        self.ymd = ymd
        self.ymdh = ymdh
        self.ymdhi = ymdhi
        self.ymdhis = ymdhis


class DataSummaryTimes:
    digits: DataSummaryTimeDigits
    strings: DataSummaryTimeStrings

    def __init__(self, time: datetime):
        parts = DateParts(time)

        self.digits = DataSummaryTimeDigits(parts=parts)
        self.strings = DataSummaryTimeStrings(parts=parts)


def iterator_to_kdv(
        items: List[Union[Tuple, List]],
        key_index=0,
        date_index=1,
        value_index=2,
        header: Tuple[str, str] = None
) -> Dict[str, List[Tuple[str, Union[int, float, str]]]]:
    """ Get Key-date-value Dict

    :param items: Iterator
    :param key_index: Index of items to make key
    :param date_index: Index of items to make date
    :param value_index: Index of items to make value
    :param header: First Item to using as heading
    """
    result = {}

    for item in items:
        key = item[key_index]
        date = item[date_index]
        value = item[value_index]

        item = (date, value)
        if key in result:
            result[key].append(item)
        else:
            if header:
                result[key] = [header, item]
                continue
            result[key] = [item]

    return result


class _KdvWithSummary(TypedDict):
    count: int
    sum: int
    average: Optional[float]
    min: int
    max: int
    series: List[Tuple[str, Union[int, float, str]]]


def iterator_to_kdv_with_summary(
        items: List[Union[Tuple, List]],
        key_index=0,
        date_index=1,
        value_index=2,
        header: Tuple[str, str] = None
) -> Dict[str, _KdvWithSummary]:
    """ Get Key-date-value Dict with Summaries
    :param items: Iterator
    :param key_index: Index of items to make key
    :param date_index: Index of items to make date
    :param value_index: Index of items to make value
    :param header: First Item to using as heading
    """
    result = {}

    for item in items:
        key = item[key_index]
        date = item[date_index]
        value = item[value_index]

        item = (date, value)
        if key in result:
            summary = result[key]
            summary['count'] = summary['count'] + 1
            summary['sum'] = summary['sum'] + value
            summary['min'] = min(summary['min'], value)
            summary['max'] = max(summary['max'], value)
            summary['series'].append(item)
        else:
            result[key] = _KdvWithSummary(
                count=1,
                sum=value,
                average=value,
                min=value,
                max=value,
                series=[item] if header is None else [header, item]
            )

    for key in result:
        summary = result[key]
        summary['average'] = summary['sum'] / summary['count']

    return result
