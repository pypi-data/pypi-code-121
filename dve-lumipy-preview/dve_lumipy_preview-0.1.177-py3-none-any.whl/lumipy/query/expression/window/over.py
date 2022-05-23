from __future__ import annotations

from typing import Iterable, Optional, Union, Any

from lumipy.common.string_utils import indent_str
from lumipy.query.expression.column.column_literal import python_to_expression
from .filter import WindowFilter
from .frame import WindowFrame
from .function import (
    FirstValue, LastValue, Lag, Lead,
    NthValue,
    CumeDist, DenseRank, Rank, NTile,
    RowNumber, PercentRank, WindowAggregate
)
from .order import WindowOrder
from .partition import WindowPartition
from ..base_sql_expression import BaseSqlExpression
from ..column.column_base import BaseColumnExpression
from ..column.column_ordering import BaseColumnOrdering
from ..sql_value_type import SqlValType


class Over(BaseSqlExpression):
    """Class representing the OVER clause in a SQL window function specification.

    """

    def __init__(
            self,
            partitions: Optional[WindowPartition],
            orders: Optional[WindowOrder],
            frame: Optional[WindowFrame],
            filter_expr: Optional[BaseColumnExpression]
    ):
        """Constructor for the Over class. User must provide at least one of a window partition object, a window order
        object or a window frame object.

        Args:
            partitions (Optional[WindowPartition]): optional window partition object.
            orders (Optional[WindowPartition]): optional window ordering object.
            frame (Optional[WindowPartition]): optional window frame objecy.
        """

        if all(x is None for x in [partitions, orders, frame]):
            raise ValueError(
                'Over objects must be created with one or more of WindowPartition, WindowOrder, '
                'or WindowFrame objects.'
            )

        self.frame = frame
        # Handle the case where these are unspecified and equal to None
        # None is replaced by a null literal node and can be used in recomposing the DAG after decomposing it
        # Expression types just pass through this function unaffected.
        self.partitions = python_to_expression(partitions)
        self.orders = python_to_expression(orders)
        self.filter_expr = python_to_expression(filter_expr)

        if self.partitions.get_type() != SqlValType.Null and not isinstance(partitions, WindowPartition):
            raise TypeError(
                f"partitions arg must be a WindowPartition instance or None. Was {type(partitions).__name__}")
        if self.orders.get_type() != SqlValType.Null and not isinstance(orders, WindowOrder):
            raise TypeError(f"orders arg must be a WindowOrder instance or None. Was {type(orders).__name__}")
        if not isinstance(frame, WindowFrame):
            raise TypeError(f"frame arg must be a WindowFrame instance. Was {type(frame).__name__}")
        if self.filter_expr.get_type() != SqlValType.Null and not isinstance(filter_expr, WindowFilter):
            raise TypeError(f"filter_expr arg must WindowFilter or None. Was {self.filter_expr.get_type()}")

        from .fn_accessors.finance import FinanceWindowFunctionAccessor
        from .fn_accessors.linreg import LinregWindowFunctionAccessor
        from .fn_accessors.metric import MetricWindowFunctionAccessor
        from .fn_accessors.stats import StatsWindowFunctionAccessor
        self.finance = FinanceWindowFunctionAccessor(self)
        self.linreg = LinregWindowFunctionAccessor(self)
        self.stats = StatsWindowFunctionAccessor(self)
        self.metric = MetricWindowFunctionAccessor(self)

        def sql_str_fn(partition, orders, frame, filter):

            if filter.get_type() != SqlValType.Null:
                filter_expr_str = filter.get_sql() + ' '
            else:
                filter_expr_str = ''

            content = [
                partition.get_sql() if partition.get_type() != SqlValType.Null else '',
                orders.get_sql() if orders.get_type() != SqlValType.Null else '',
                frame.get_sql() if frame.get_type() != SqlValType.Null else ''
            ]

            content_str = '\n'.join(c for c in content if c != '')

            return f"{filter_expr_str}OVER(\n{indent_str(content_str, n=6)}\n  )"

        super().__init__(
            'window',
            sql_str_fn,
            lambda *args: True,
            lambda *args: SqlValType.Window,
            self.partitions,
            self.orders,
            self.frame,
            self.filter_expr
        )

    def first(self, expression: BaseColumnExpression) -> FirstValue:
        """Get the value of an expression for the first row in the window.

        Args:
            expression (BaseColumnExpression): column expression to evaluate at the first row.

        Returns:
            FirstValue: first window function instance representing this expression.
        """
        return FirstValue(self, expression)

    def last(self, expression: BaseColumnExpression) -> LastValue:
        """Get the value of an expression for the last row in the window.

        Args:
            expression (BaseColumnExpression): column expression to evaluate at the last row.

        Returns:
            LastValue: last window function instance representing this expression.
        """
        return LastValue(self, expression)

    def lag(self, expression: BaseColumnExpression, offset: Optional[int] = 1, default: Optional[Any] = None) -> Lag:
        """Apply a lag window expression: get the value of an expression n places behind the current row in the window.

        For example for n = 1 evaluated at row 3 it will yield the value at row 2. If the lag row is out of the window
        range a default value will be returned.

        Args:
            expression (BaseColumnExpression): the column expression to evaluate with lag.
            offset (Optional[int]): the number of places behind to evaluate at (defaults to 1)
            default (Optional[Any]): the default value to assign to out of range lag rows (defaults to None, which is
            considred to be equal to NULL in SQL)

        Returns:
            Lag: lag window function expression instance.
        """
        return Lag(self, expression, offset, default)

    def lead(self, expression: BaseColumnExpression, offset: Optional[int] = 1,
             default: Optional[Union[Any]] = None) -> Lead:
        """Apply a lead window expression: get the value of an expression n places in front the current row in the window.

        For example for n = 1 evaluated at row 2 it will yield the value at row 3. If the lead row is out of the window
        range a default value will be returned.

        Args:
            expression (BaseColumnExpression): the column expression to evaluate with lead.
            offset (Optional[int]): the number of places behind to evaluate at (defaults to 1)
            default (Optional[Any]): the default value to assign to out of range lead rows (defaults to None, which is
            considred to be equal to NULL in SQL)

        Returns:
            Lead: lead window function expression instance.
        """
        return Lead(self, expression, offset, default)

    def nth_value(self, expression: BaseColumnExpression, n: int) -> NthValue:
        """Apply an nth value expression: get the value of the expression at position n in the window.

        Args:
            expression (BaseColumnExpression): the expression to evaluate at the nth row
            n (int): the value of n to use.

        Returns:
            NthValue: nth value window function expression instance.
        """
        return NthValue(self, expression, n)

    def mean(self, expression: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean (AVG) aggregation expression: get the mean value of the expression in a window.

        Args:
            expression (BaseColumnExpression): expression to take the mean of in the window.

        Returns:
            WindowMean: mean value window function expression instance.
        """
        return WindowAggregate(self, expression.mean())

    def count(self, expression: BaseColumnExpression) -> WindowAggregate:
        """Apply a count aggregation expression: count the number of rows where the expression is not null.

        Args:
            expression (BaseColumnExpression): expression to evaluate in the count.

        Returns:
            WindowCount: count window function.
        """
        # todo: check nulls aren't counted.
        return WindowAggregate(self, expression.count())

    def max(self, expression: BaseColumnExpression) -> WindowAggregate:
        """Apply a max aggregation expression: get the max value of the expression in a window.

        Args:
            expression (BaseColumnExpression): expression to take the max of in the window.

        Returns:
            WindowMax: max value window function expression instance.
        """
        return WindowAggregate(self, expression.max())

    def min(self, expression: BaseColumnExpression) -> WindowAggregate:
        """Apply a min aggregation expression: get the min value of the expression in a window.

        Args:
            expression (BaseColumnExpression): expression to take the min of in the window.

        Returns:
            WindowMin: min value window function expression instance.
        """
        return WindowAggregate(self, expression.min())

    def sum(self, expression: BaseColumnExpression) -> WindowAggregate:
        """Apply a sum aggregation expression: get the value of the expression summed over a window.

        Args:
            expression (BaseColumnExpression): expression to take the sum of in the window.

        Returns:
            WindowSum: sum value window function expression instance.
        """
        return WindowAggregate(self, expression.sum())

    def prod(self, expression):
        from lumipy.query.expression.column_op.aggregation_op import CumeProd
        return WindowAggregate(self, CumeProd(expression))

    def cume_dist(self) -> CumeDist:
        """Apply a cumulative distribution ranking expression: position of an expression's value in the cumulative
        distribution of the expression normalised between 0 and 1.

        Returns:
            CumeDist: cumulative dist window function expression instance.
        """
        return CumeDist(self)

    def dense_rank(self) -> DenseRank:
        """Apply a dense rank expression to the window. Equal values (in the sort by column(s)) will have the same value,
        the next value in rank after is not skipped in the case of a tie (in contrast to the rank function).

        Returns:
            Rank: dense rank window function expression object.
        """
        return DenseRank(self)

    def ntile(self, n: int) -> NTile:
        """Apply an N tile expression to the window. This will assign in integer label to each row in the window such
        that the window is partitioned into n-many groups in a tiling fashion.

        Args:
            n (int): number of tiles.

        Returns:
            NTile: n tile window function expression object.
        """
        return NTile(self, n)

    def rank(self) -> Rank:
        """Apply a rank expression to the window. Equal values (in the sort by column(s)) will have the same value,
        the next value in rank after is skipped in the case of a tie.

        Returns:
            Rank: rank window function expression object.
        """
        return Rank(self)

    def row_number(self) -> RowNumber:
        """Apply a row number expression to the window. This will return the in-window row number value as a new column.

        Returns:
            RowNumber: row number window function expression object.
        """
        return RowNumber(self)

    def percent_rank(self) -> PercentRank:
        """Apply a percent rank expression to the window. This will return the rank of a row as a number between 0 and 1

        Returns:
            PercentRank: percent rank window function expression object.
        """
        return PercentRank(self)

    def filter(self, expression: BaseColumnExpression) -> Over:
        """Apply a filter expression to the window function. The filter will remove rows that evaluate to false and
        they will therefore be ignored in the window function calculation.

        Args:
            expression (BaseColumnExpression): filter expression to use. Must evaluate to a boolean.

        Returns:
            FilteredOver: FilteredOver instance that represents the given OVER with the given filter expression.
        """
        if self.filter_expr.get_type() == SqlValType.Null:
            filter_expr = WindowFilter(expression)
        else:
            filter_expr = WindowFilter(self.filter_expr.get_expression() & expression)

        return Over(self.partitions, self.orders, self.frame, filter_expr)


def window(
        groups: Optional[Union[Iterable[BaseColumnExpression], BaseColumnExpression]] = None,
        orders: Optional[Union[Iterable[BaseColumnOrdering], BaseColumnOrdering]] = None,
        lower: Optional[int, None] = None,
        upper: Optional[int, None] = 0
) -> Over:
    """Build a window that will be used with window functions.
    Windows are a particular partition, and/or a sliding range of rows around a central row with an optional ordering.
    If no ordering is applied it'll just evaluate in RowID order.

    Once built a window can be used to build window functions by calling methods on the window object such as sum(),
    first() or rank().

    Args:
        groups (Optional[Union[Iterable[BaseColumnExpression], BaseColumnExpression]]): one of either a list of column
            expressions, a single column expression or None. None means there is no partition in the windowing (default).
        orders (Optional[Union[Iterable[BaseColumnOrdering], BaseColumnOrdering]]): one of either a list of column
            expression orderings, a single one or None. None means that the window will be sorted by row number (default).
        lower (Optional[Union[int, None]]): lower (start) limit of the window as a number of rows before the current
            row. If None then the window is unbounded below and has no lower limit, if zero it is the current row (default is None).
        upper (Optional[Union[int, None]]): upper (end) limit of the window as a number of rows after the current row.
            If None then the window is unbounded above and has no upper limit, if 0 it is the current row (default is 0).

    Returns:
        Over: the over instance representing the window defined by the arguments.
    """
    if isinstance(groups, (list, tuple)) and len(groups) > 0:
        partition = WindowPartition(*groups)
    elif groups is not None:
        partition = WindowPartition(groups)
    else:
        partition = None

    if isinstance(orders, (list, tuple)) and len(orders) > 0:
        ordering = WindowOrder(*orders)
    elif orders is not None:
        ordering = WindowOrder(orders)
    else:
        ordering = None

    frame = WindowFrame.create(lower, upper)

    return Over(partition, ordering, frame, None)
