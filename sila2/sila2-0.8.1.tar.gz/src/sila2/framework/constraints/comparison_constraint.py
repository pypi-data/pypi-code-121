from __future__ import annotations

import math
from abc import ABC
from datetime import datetime, time
from typing import Callable, TypeVar, Union

from sila2.framework.abc.constraint import Constraint
from sila2.framework.data_types.date import Date, SilaDateType
from sila2.framework.data_types.integer import Integer
from sila2.framework.data_types.real import Real
from sila2.framework.data_types.string import String
from sila2.framework.data_types.time import Time
from sila2.framework.data_types.timestamp import Timestamp

T = TypeVar("T", bound=Union[str, int, float, SilaDateType, time, datetime])
ComparableType = Union[str, int, float, datetime]


class ComparisonConstraint(Constraint[T], ABC):
    comparison_operator: Callable[[T, T], bool]
    base_type: Union[String, Integer, Real, Date, Time, Timestamp]
    reference_value: ComparableType
    value_from_xml: str

    def __init__(
        self,
        base_type: Union[String, Integer, Real, Date, Time, Timestamp],
        comparison_operator: Callable[[T, T], bool],
        value_from_xml: str,
    ):
        self.base_type = base_type
        self.comparison_operator = comparison_operator
        self.value_from_xml = value_from_xml
        self.reference_value = self._parse_value_from_string(value_from_xml)

    def validate(self, value: T) -> bool:
        return self.comparison_operator(self.reference_value, self._convert_value_for_comparison(value))

    def _convert_value_for_comparison(self, value: T) -> ComparableType:
        if isinstance(self.base_type, (String, Integer, Real, Timestamp)):
            return value
        if isinstance(self.base_type, Date):
            d, tz = value
            return datetime(year=d.year, month=d.month, day=d.day, tzinfo=tz)
        if isinstance(self.base_type, Time):
            return datetime(
                year=2000,
                month=1,
                day=1,
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                tzinfo=value.tzinfo,
            )
        else:
            raise NotImplementedError  # should never happen

    def _parse_value_from_string(self, value: str) -> ComparableType:
        if isinstance(self.base_type, String):
            return value
        if isinstance(self.base_type, Integer):
            # scientific notation like 3e4 for 30000 is allowed for integers
            parsed_value = float(value)
            if not math.isfinite(parsed_value):
                raise ValueError(f"Integer values must be finite, got {value}")  # should never happen
            return parsed_value
        if isinstance(self.base_type, Real):
            return float(value)
        if isinstance(self.base_type, Date):
            d, tz = Date.from_string(value)
            return datetime(year=d.year, month=d.month, day=d.day, tzinfo=tz)
        if isinstance(self.base_type, Time):
            t = Time.from_string(value)
            return datetime(year=2000, month=1, day=1, hour=t.hour, minute=t.minute, second=t.second, tzinfo=t.tzinfo)
        if isinstance(self.base_type, Timestamp):
            return Timestamp.from_string(value)
        else:
            raise NotImplementedError  # should never happen

    def __repr__(self) -> str:
        if isinstance(self.base_type, (Integer, Real)):
            return f"{self.__class__.__name__}({self.reference_value})"
        return f"{self.__class__.__name__}({self.value_from_xml!r})"
