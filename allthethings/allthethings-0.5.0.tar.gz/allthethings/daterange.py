from __future__ import annotations

import itertools
import re
from datetime import date, timedelta
from typing import Optional, List, Tuple, Iterator

from .dates import at_end_of_month, read_date
from .ranges import range_incl


class DateRange:
    DAYS_PATTERN = re.compile(r'\s*DAYS\((\d+)\)\s*')

    @classmethod
    def maybe_timedelta(cls, value: str) -> Optional[timedelta]:
        m = cls.DAYS_PATTERN.match(value)
        if m:
            return timedelta(days=int(m.group(1)))
        return None

    @staticmethod
    def _date_or_begin_of_month(v: str) -> date:
        components = v.split('-')
        if len(components) == 2:
            year, month = components
            return date(int(year), int(month), 1)
        else:
            return read_date(v)

    @staticmethod
    def _date_or_end_of_month(v: str) -> date:
        components = v.split('-')
        if len(components) == 2:
            year, month = components
            d: date = date(int(year), int(month), 1)
            return at_end_of_month(d)
        else:
            return read_date(v)

    def __init__(self, date_range: str = ""):
        self._subranges: List[Tuple[Optional[date], Optional[date]]] = []
        if not date_range:
            return
        components = date_range.translate(str.maketrans('', '', ' ')).split(',')
        for component in components:
            range_components = component.split('..')
            if len(range_components) == 1:
                parts = component.split('-')
                if len(parts) == 2:
                    year, month = parts
                    year = int(year)
                    month = int(month)
                    lower: date = date(year, month, 1)
                    upper = at_end_of_month(lower)
                    self._subranges.append((lower, upper))
                else:
                    d = read_date(component)
                    self._subranges.append((d, d))
            elif len(range_components) == 2:
                c1, c2 = range_components
                d1 = self.maybe_timedelta(c1) or (c1 and self._date_or_begin_of_month(c1) or None)
                parser = self._date_or_begin_of_month if isinstance(d1, timedelta) else self._date_or_end_of_month
                d2 = self.maybe_timedelta(c2) or (c2 and parser(c2) or None)
                if isinstance(d1, timedelta):  # flip so time delta will always be d2
                    d1, d2 = d2, -d1
                if isinstance(d2, timedelta):
                    if isinstance(d1, timedelta) or d1 is None:
                        raise ValueError("date range cannot be composed only from time-deltas")
                    d1, d2 = sorted([d1 + d2, d1])
                self._subranges.append((d1, d2))

    def __contains__(self, item) -> bool:
        d = read_date(item)
        for d1, d2 in self._subranges:
            if d1 and d2:
                if d1 <= d <= d2:
                    return True
            elif d1:
                if d1 <= d:
                    return True
            else:
                if d <= d2:
                    return True
        return False

    def __eq__(self, other):
        if isinstance(other, date):
            return self._cmp(other) == 0
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, date):
            return self._cmp(other) <= 0
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, date):
            return self._cmp(other) < 0
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, date):
            return self._cmp(other) >= 0
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, date):
            return self._cmp(other) > 0
        return NotImplemented

    def _cmp(self, other: date):
        if (max_ := self.max) is not None and max_ < other:  # pylint: disable=E0601
            return -1
        if (min_ := self.min) is not None and min_ > other:  # pylint: disable=E0601
            return 1
        return 0

    @property
    def min(self) -> Optional[date]:
        if any(lower is None for lower, _ in self._subranges) or not self._subranges:
            return None
        return min(lower for lower, _ in self._subranges)

    @property
    def max(self) -> Optional[date]:
        if any(upper is None for _, upper in self._subranges) or not self._subranges:
            return None
        return max(upper for _, upper in self._subranges)

    def iter(self, lower=None, upper=None) -> Iterator[date]:
        lower = lower and read_date(lower) or self.min or None
        upper = upper and read_date(upper) or self.max or None

        if not lower or not upper:
            raise ValueError('no lower or upper bound')

        for d in range_incl(lower, upper):
            if d in self:
                yield d

    def itermonths(self) -> Iterator[DateRange]:
        for _key, group in itertools.groupby(iter(self), lambda d: d.month):
            yield DateRange(','.join(sorted(str(d) for d in group)))

    def __iter__(self) -> Iterator[date]:
        if not self._subranges:
            return
        min_ = self.min
        max_ = self.max
        if min_ is None or max_ is None:
            raise ValueError("open range")
        yield from self.iter(min_, max_)

    def _subranges_str(self) -> Iterator[str]:
        for lower, upper in self._subranges:
            if lower is None:
                yield f"..{upper}"
            elif upper is None:
                yield f"{lower}.."
            elif lower == upper:
                yield f"{lower}"
            else:
                yield f"{lower}..{upper}"

    def __str__(self) -> str:
        return ','.join(self._subranges_str())

    def __bool__(self):
        return bool(self._subranges)
