from numbers import Real
from typing import Optional

from ._InvalidStateError import InvalidStateError


class Interval:
    """
    Class which represents a numeric interval.
    E.g. [-1:1) or (4.333:12.78]

    Types of interval:
        - Total: contains all numbers.
        - Empty: contains no numbers.
        - Open-Upper: Contains all numbers above a certain value.
        - Open-Lower: Contains all numbers below a certain value.
        - Singular: Contains a single number.
        - Exclude-Value: Contains all numbers except a single value.
        - Outside: Contains all numbers that are NOT between two values.
        - Inside: The standard interval. Contains all numbers between two values.

    Manual manipulation of the members of this class may result in an
    InvalidStateError. Prefer to use the static constructor methods instead.
    """
    def __init__(self,
                 lower: Optional[Real],
                 upper: Optional[Real],
                 lower_inclusive: bool = True,
                 upper_inclusive: bool = False):
        self._lower: Optional[Real] = lower
        self._upper: Optional[Real] = upper
        self._lower_inclusive: bool = lower_inclusive
        self._upper_inclusive: bool = upper_inclusive

    def __contains__(self, value: Real) -> bool:
        if self.is_total():
            return True
        elif self.is_empty():
            return False
        elif self.is_open_upper():
            return self._above_lower(value)
        elif self.is_open_lower():
            return self._below_upper(value)
        elif self.is_singular():
            return value == self._lower
        elif self.is_exclude_value():
            return value != self._lower
        elif self.is_outside():
            return self._above_lower(value) or self._below_upper(value)
        elif self.is_inside():
            return self._above_lower(value) and self._below_upper(value)
        else:
            # Invalid state
            raise InvalidStateError("Misconfigured Interval")

    def __str__(self):
        # Format string for lower bound
        lower: str = "[" if self._lower_inclusive else "("
        if self._lower is not None:
            lower += str(self._lower)

        # Format string for upper bound
        upper: str = str(self._upper) if self._upper is not None else ""
        upper += "]" if self._upper_inclusive else ")"

        # Format the string parts into the whole
        if self.is_outside():
            return upper + lower
        elif self.is_singular():
            return lower + "]"
        elif self.is_exclude_value():
            return lower + ")"
        else:
            return lower + ":" + upper

    def is_total(self) -> bool:
        """
        Whether this interval is a total interval (contains
        all points).
        """
        return self._lower is None and self._upper is None and self._upper_inclusive and self._lower_inclusive

    def is_empty(self) -> bool:
        """
        Whether this interval is an empty interval (contains
        no points).
        """
        return self._lower is None and self._upper is None and not self._upper_inclusive and not self._lower_inclusive

    def is_open_lower(self) -> bool:
        """
        Whether this interval is an open-lower interval.
        """
        return self._upper is not None and self._lower is None and self._lower_inclusive

    def is_open_upper(self) -> bool:
        """
        Whether this interval is an open-upper interval.
        """
        return self._lower is not None and self._upper is None and self._upper_inclusive

    def is_half_open(self) -> bool:
        """
        Whether this interval is half-open.
        """
        return self.is_open_lower() or self.is_open_upper()

    def is_singular(self) -> bool:
        """
        Whether this interval is a singular interval (only
        includes one value).
        """
        return self._lower is not None and self._upper is not None and self._lower == self._upper \
            and self._upper_inclusive and self._lower_inclusive

    def is_exclude_value(self) -> bool:
        """
        Whether this interval is an exclude-value interval
        (includes all values except one).
        """
        return self._lower is not None and self._upper is not None and self._lower == self._upper \
            and not self._upper_inclusive and not self._lower_inclusive

    def is_outside(self) -> bool:
        """
        Whether this interval is an outside interval.
        """
        return self._lower is not None and self._upper is not None and self._lower > self._upper

    def is_inside(self) -> bool:
        """
        Whether this interval is a standard inside interval. Included for completeness.
        """
        return self._lower is not None and self._upper is not None and self._upper > self._lower

    def inverse(self) -> 'Interval':
        """
        Gets the inverse interval to this one (contains all points
        this one doesn't).
        """
        return Interval(self._upper, self._lower, not self._upper_inclusive, not self._lower_inclusive)

    def _above_lower(self, value: Real) -> bool:
        """
        Returns whether the given value is included by the
        lower bound. Assumes the lower bound exists.

        :param value:   The value to check.
        :return:        True if the value is contained by the
                        lower bound, False if not.
        """
        return value >= self._lower if self._lower_inclusive else value > self._lower

    def _below_upper(self, value: Real) -> bool:
        """
        Returns whether the given value is included by the
        upper bound. Assumes the upper bound exists.

        :param value:   The value to check.
        :return:        True if the value is contained by the
                        upper bound, False if not.
        """
        return value <= self._upper if self._upper_inclusive else value < self._upper

    @staticmethod
    def total() -> 'Interval':
        """
        Creates a total interval.
        """
        return Interval(None, None, True, True)

    @staticmethod
    def empty() -> 'Interval':
        """
        Creates an empty interval.
        """
        return Interval(None, None, False, False)

    @staticmethod
    def open_upper(lower: Real, lower_inclusive: bool = True) -> 'Interval':
        """
        Creates an open-upper interval.

        :param lower:               The lower-bound of the interval.
        :param lower_inclusive:     Whether the lower bound is inclusive.
        """
        return Interval(lower, None, lower_inclusive, True)

    @staticmethod
    def open_lower(upper: Real, upper_inclusive: bool = False) -> 'Interval':
        """
        Creates an open-lower interval.

        :param upper:               The upper bound of the interval.
        :param upper_inclusive:     Whether the upper bound is inclusive.
        """
        return Interval(None, upper, True, upper_inclusive)

    @staticmethod
    def singular(value: Real) -> 'Interval':
        """
        Creates a singular interval.

        :param value:   The single contained value.
        """
        return Interval(value, value, True, True)

    @staticmethod
    def exclude_value(value: Real) -> 'Interval':
        """
        Creates an exclude-value interval.

        :param value:   The single excluded value.
        """
        return Interval(value, value, False, False)

    @staticmethod
    def inside(value1: Real, value2: Real, lower_inclusive: bool = True, upper_inclusive: bool = False) -> 'Interval':
        """
        Creates an inside interval from possibly-unordered values.

        :param value1:              One bound of the inside interval.
        :param value2:              The other bound of the inside interval.
        :param lower_inclusive:     Whether the lower bound should be inclusive.
        :param upper_inclusive:     Whether the upper bound should be inclusive.
        """
        if value1 == value2:
            raise ValueError("Require unequal bounds for inside interval")

        return Interval(min(value1, value2), max(value1, value2), lower_inclusive, upper_inclusive)

    @staticmethod
    def outside(value1: Real, value2: Real, lower_inclusive: bool = True, upper_inclusive: bool = False) -> 'Interval':
        """
        Creates an outside interval from possibly-unordered values.

        :param value1:              One bound of the outside interval.
        :param value2:              The other bound of the outside interval.
        :param lower_inclusive:     Whether the lower bound should be inclusive.
        :param upper_inclusive:     Whether the upper bound should be inclusive.
        """
        if value1 == value2:
            raise ValueError("Require unequal bounds for outside interval")

        return Interval(max(value1, value2), min(value1, value2), lower_inclusive, upper_inclusive)
