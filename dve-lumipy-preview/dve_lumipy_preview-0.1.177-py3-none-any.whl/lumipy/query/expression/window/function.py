from __future__ import annotations

from abc import abstractmethod
from typing import Callable

from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import python_to_expression
from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn
from lumipy.query.expression.sql_value_type import SqlValType


class BaseWindowFunction(BaseColumnExpression):
    """Abstract base class for all window function expressions.

    """

    @abstractmethod
    def __init__(
            self,
            name: str,
            window: 'Over',
            sql_str_fn: Callable,
            type_check_fn: Callable,
            data_type_fn: Callable,
            *values: BaseColumnExpression
    ):
        """Constructor for the BaseWindowFunction class.

        Args:
            name (str): name of the expression type.
            window (Over): window defininition (OVER clause)
            sql_str_fn (Callable): function that generates the corresponding SQL string from input expressions.
            type_check_fn (Callable): function that checks the input expression types.
            data_type_fn (Callable): function that defines the output type of this expression.
            *values (BaseColumnExpression): the input values to the expression.
        """

        values = [python_to_expression(v) for v in values]

        if len(values) > 0:
            source_table_hash = values[0].source_table_hash()
        else:
            source_table_hash = window.get_col_dependencies()[0].source_table_hash()

        super().__init__(
            source_table_hash,
            sql_str_fn,
            type_check_fn,
            data_type_fn,
            name,
            window,
            *values
        )


class FirstValue(BaseWindowFunction):

    def __init__(self, window, expression):
        super().__init__(
            "first value",
            window,
            lambda x, y: f"FIRST_VALUE({y.get_sql()}) {x.get_sql()}",
            lambda x, y: x == SqlValType.Window,
            lambda x, y: y,
            expression
        )


class LastValue(BaseWindowFunction):

    def __init__(self, window, expression):
        super().__init__(
            "last value",
            window,
            lambda x, y: f"LAST_VALUE({y.get_sql()}) {x.get_sql()}",
            lambda x, y: x == SqlValType.Window,
            lambda x, y: y,
            expression
        )


class Lag(BaseWindowFunction):

    def __init__(self, window, expression, offset, default):
        super().__init__(
            "lag value",
            window,
            lambda x, y, z, w: f"LAG({y.get_sql()}, {z.get_sql()}, {w.get_sql()}) {x.get_sql()}",
            lambda x, y, z, w: x == SqlValType.Window,
            lambda x, y, z, w: y,
            expression,
            offset,
            default
        )


class Lead(BaseWindowFunction):

    def __init__(self, window, expression, offset, default):
        super().__init__(
            "lead value",
            window,
            lambda x, y, z, w: f"LEAD({y.get_sql()}, {z.get_sql()}, {w.get_sql()}) {x.get_sql()}",
            lambda x, y, z, w: x == SqlValType.Window,
            lambda x, y, z, w: y,
            expression,
            offset,
            default
        )


class NthValue(BaseWindowFunction):

    def __init__(self, window, expression, n):
        super().__init__(
            'nth value',
            window,
            lambda x, y, z: f"NTH_VALUE({y.get_sql()}, {z.get_sql()}) {x.get_sql()}",
            lambda x, y, z: x == SqlValType.Window and z == SqlValType.Int,
            lambda x, y, z: y,
            expression,
            n
        )


class CumeDist(BaseWindowFunction):

    def __init__(self, window):
        super().__init__(
            'window cume dist',
            window,
            lambda x: f"CUME_DIST() {x.get_sql()}",
            lambda x: x == SqlValType.Window,
            lambda x: SqlValType.Double
        )


class DenseRank(BaseWindowFunction):

    def __init__(self, window):
        super().__init__(
            'window dense rank',
            window,
            lambda x: f"DENSE_RANK() {x.get_sql()}",
            lambda x: x == SqlValType.Window,
            lambda x: SqlValType.Double
        )


class NTile(BaseWindowFunction):

    def __init__(self, window, n):
        super().__init__(
            'window ntile',
            window,
            lambda x, y: f"NTILE({y.get_sql()}) {x.get_sql()}",
            lambda x, y: x == SqlValType.Window and y == SqlValType.Int,
            lambda x, y: SqlValType.Int,
            n
        )


class Rank(BaseWindowFunction):

    def __init__(self, window):
        super().__init__(
            'window rank',
            window,
            lambda x: f"RANK() {x.get_sql()}",
            lambda x: x == SqlValType.Window,
            lambda x: SqlValType.Int
        )


class RowNumber(BaseWindowFunction):

    def __init__(self, window):
        super().__init__(
            'window rank',
            window,
            lambda x: f"ROW_NUMBER() {x.get_sql()}",
            lambda x: x == SqlValType.Window,
            lambda x: SqlValType.Int
        )


class PercentRank(BaseWindowFunction):

    def __init__(self, window):
        super().__init__(
            'window rank',
            window,
            lambda x: f"PERCENT_RANK() {x.get_sql()}",
            lambda x: x == SqlValType.Window,
            lambda x: SqlValType.Double
        )


class WindowAggregate(BaseWindowFunction):

    def __init__(self, window, expression):

        if not isinstance(expression, BaseAggregateColumn):
            raise TypeError("Input expression must be an aggregate operation.")

        super().__init__(
            'window ' + expression.get_op_name(),
            window,
            lambda x, y: f'{y.get_sql()} {x.get_sql()}',
            lambda x, y: x == SqlValType.Window,
            lambda x, y: y,
            expression
        )


