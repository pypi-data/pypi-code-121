"""
@package text.period

Module for describing textually periods
"""

# Built-in packages
from __future__ import annotations
from typing import Sequence, Union

# Own package
from mfire.settings import get_logger, Settings, TEMPLATES_FILENAMES
from mfire.utils.json_utils import JsonFile
from mfire.utils.date import Datetime, Period

# Logging
LOGGER = get_logger(name="text.period.mod", bind="text.period")

DATES = JsonFile(TEMPLATES_FILENAMES[Settings().language]["date"]).load()


class PeriodDescriber:
    """PeriodDescriber: Class for describing periods or sequences of periods.
    If a single period is given, the class will simply use the period.describe
    method.
    Else, if a sequence of periods is given, the period describer will first
    try to reduce the number of periods by merging those which extends themselves,
    and then will use the period.describe method on all the reduced periods.

    Args:
        request_time (Datetime): Point of view used for describing the
            given periods
    """

    def __init__(self, request_time: Datetime) -> None:
        self.request_time = Datetime(request_time)

    def reduce(self, periods: Sequence[Period]) -> Sequence[Period]:
        """reduce: method which reduces a sequence of periods to another sequence
        of periods, where those new periods are a merging of previous periods that
        extends themselves.

        Args:
            periods (Sequence[Period]): Sequence of periods to reduce.

        Returns:
            Sequence[Period]: Reduced periods.
        """
        if len(periods) == 0:
            return []

        new_periods = []
        current_period = periods.pop(0)
        for period in periods:
            if period.extends(current_period, request_time=self.request_time):
                current_period = current_period.union(period)
            else:
                new_periods += [current_period]
                current_period = period
        new_periods += [current_period]
        return new_periods

    def describe_multi(self, periods: Sequence[Period]) -> str:
        """describe_multi: takes a sequence of periods and returns
        a textual description of this sequence of periods.

        Args:
            periods (Sequence[Period]): Sequence of periods to describe.

        Returns:
            str: textual description of the given sequence.
        """
        reduced = self.reduce(periods)
        if len(reduced) == 1:
            return reduced[0].describe(self.request_time)
        return (
            ", ".join(p.describe(self.request_time) for p in reduced[:-1])
            + " et "
            + reduced[-1].describe(self.request_time)
        )

    def describe(self, periods: Union[Sequence[Period], Period]) -> str:
        """describe: method for describing periods or sequences of periods.
        If a single period is given, the method will simply use the period.describe
        method.
        Else, if a sequence of periods is given, the period describer will first
        try to reduce the number of periods by merging those which extends themselves,
        and then will use the period.describe method on all the reduced periods.

        Args:
            periods (Union[Sequence[Period], Period]): Periods to describe.

        Returns:
            str: Textual description of given period(s)
        """
        if isinstance(periods, Period):
            return periods.describe(self.request_time)
        return self.describe_multi(periods)
