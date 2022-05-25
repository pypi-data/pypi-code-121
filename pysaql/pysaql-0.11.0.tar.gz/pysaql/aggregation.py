"""Contains aggregation function definitions"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union

from .enums import Order
from .function import Function, NullaryFunction
from .scalar import Scalar
from .util import stringify_list


class FieldAggregation(Function):
    """Field aggregation function"""

    def __init__(self, field: Scalar) -> None:
        """Initializer

        Args:
            field: Reference to a field to aggregate

        """
        super().__init__(field)


class WindowFunction(Function):
    """Window function to calculate values for each partition in a group

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_windowing.htm
    """

    def over(
        self,
        row_range: Tuple[Optional[int], Optional[int]],
        reset_groups: Union[str, Sequence[Scalar]],
        order_by: Sequence[Union[Scalar, Tuple[Scalar, Order]]],
    ) -> WindowFunction:
        """Set the windowing function parameters

        Args:
            row_range: Defines the window to aggregate within the reset group
            reset_groups: The column(s) which reset windowing aggregation when their
                value(s) change. A reset group of all indicates no reset boundaries for
                the window aggregation.
            order_by: Specify column(s) by which to sort. This orders the rows before
                the window function gets evaluated.

        Returns:
            self

        """
        self._row_range = row_range
        self._reset_groups = reset_groups
        self._order_by = [order_by] if isinstance(order_by, Scalar) else order_by
        return self

    def to_string(self) -> str:
        """Cast the window function to a string

        Returns:
            SAQL string

        """
        s = super().to_string()

        if (
            getattr(self, "_row_range", None)
            and getattr(self, "_reset_groups", None)
            and getattr(self, "_order_by", None)
        ):
            start = "" if self._row_range[0] is None else self._row_range[0]
            stop = "" if self._row_range[1] is None else self._row_range[1]
            row_range = f"[{start}..{stop}]"

            reset_groups = (
                [self._reset_groups]
                if isinstance(self._reset_groups, str)
                else self._reset_groups
            )

            order_by = []
            for clause in self._order_by:
                if isinstance(clause, Scalar):
                    order_by.append(f"{clause} asc")
                else:
                    order_by.append(f"{clause[0]} {clause[1]}")

            s = f"{s} over ({row_range} partition by {stringify_list(reset_groups)} order by {stringify_list(order_by)})"

        return s


class count(NullaryFunction, WindowFunction):
    """Returns the number of rows that match the query criteria."""

    pass


class avg(FieldAggregation, WindowFunction):
    """Returns the average of the values of a measure field."""

    pass


average = avg


class min(FieldAggregation, WindowFunction):
    """Returns the minimum value of a measure field."""

    pass


class max(FieldAggregation, WindowFunction):
    """Returns the maximum value of a measure field."""

    pass


class median(FieldAggregation, WindowFunction):
    """Returns the median value of a measure field."""

    pass


class sum(FieldAggregation, WindowFunction):
    """Returns the sum of a numeric field."""

    pass


class unique(FieldAggregation):
    """Returns the count of unique values."""

    pass


class first(FieldAggregation):
    """Returns the first value for the specified field."""

    pass


class last(FieldAggregation):
    """Returns the last value in the tuple for the specified field."""

    pass


class rank(NullaryFunction, WindowFunction):
    """Assigns rank based on order

    Repeats rank when the value is the same, and skips as many on the next non-match.
    """

    pass


class dense_rank(NullaryFunction, WindowFunction):
    """Same as rank() but doesn't skip values on previous repetitions."""

    pass


class cume_dist(NullaryFunction, WindowFunction):
    """Calculates the cumulative distribution (relative position) of the data in the reset group."""

    pass


class row_number(NullaryFunction, WindowFunction):
    """Assigns a number incremented by 1 for every row in the reset group."""

    pass
