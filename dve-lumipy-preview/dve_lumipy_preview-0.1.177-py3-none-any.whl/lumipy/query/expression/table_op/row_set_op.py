from typing import Union

import lumipy.query.expression.table_op.group_aggregate_op
import lumipy.query.expression.table_op.limit_op
import lumipy.query.expression.table_op.order_by_op
import lumipy.query.expression.table_op.select_op
import lumipy.query.expression.table_op.where_op
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.common.string_utils import indent_str

table_types = Union['SelectTableExpression', 'WhereTableExpression', 'GroupByAggregation', 'RowSetOp']


class RowSetOp(BaseTableExpression):
    """Class representing a row set operation such as 'union all', 'union', 'intersect', 'except'.

    """

    def __init__(
            self,
            set_op_str,
            top: table_types,
            bottom: table_types
    ):

        self._set_op_str = set_op_str

        top_type = type(top)
        bottom_type = type(bottom)
        supported = [
            lumipy.query.expression.table_op.select_op.SelectTableExpression,
            lumipy.query.expression.table_op.where_op.WhereTableExpression,
            lumipy.query.expression.table_op.group_aggregate_op.GroupByAggregation,
            RowSetOp
        ]

        if top_type not in supported:
            supported_str = ", ".join([t.__name__ for t in supported])
            raise TypeError(
                f"Top input to {self._set_op_str} was not a supported type. Was {type(top).__name__} "
                f"but expects one of the following: {supported_str}."
            )
        if bottom_type not in supported:
            supported_str = ", ".join([t.__name__ for t in supported])
            raise TypeError(
                f"Bottom input to {self._set_op_str} was not a supported type. Was {type(bottom).__name__} "
                f"but expects one of the following: {supported_str}."
            )

        # Columns on the row set ops are just the top input columns
        # HC will throw if they're different in number, otherwise will concat
        if len(top.get_columns()) != len(bottom.get_columns()):
            raise ValueError(
                f"Input tables to {self._set_op_str} must have the same number of columns. "
                f"Was {len(top.get_columns())} vs {len(bottom.get_columns())}."
            )

        self._top = top
        self._bottom = bottom

        super().__init__(
            top.get_columns(),
            top.get_client(),
            self._set_op_str,
            None,
            top.get_source_table(),
            top,
            bottom
        )

    def get_table_sql(self):
        """Get the SQL string for the table expression only. Not including the @/@@ var assignments.

        Returns:
            str: the table SQL string.
        """
        top_sql = self._top.get_table_sql()
        op = self._set_op_str.upper()
        bottom_sql = self._bottom.get_table_sql()

        if isinstance(self._bottom, RowSetOp) and 'union' not in self._bottom._set_op_str:
            bottom_sql = indent_str(bottom_sql)

        return f"\n{top_sql}" \
               f"\n  {op}" \
               f"\n{bottom_sql}"

    def order_by(self, *order_bys):
        """Apply an order by expression to this table expression given a collection of column ordering expressions.

        Sort a table's rows according to a collection of columns/functions of columns.

        Args:
            *order_bys:column ordering expression args in teh order they are to be applied.

        Returns:
            OrderedTableExpression: OrderedTableExpression instance representing the ordering applied to this table
            expression.
        """
        return lumipy.query.expression.table_op.order_by_op.OrderedTableExpression(self, *order_bys)

    def limit(self, limit: int):
        """Apply a limit expression to this table.

        Limit will take the first n-many rows of the table.

        Args:
            limit (int): the limit value

        Returns:
            LimitTableExpression: LimitTableExpression instance representing the limit expression applied to this table
            expression.
        """
        return lumipy.query.expression.table_op.limit_op.LimitTableExpression(self, limit)

    def union(self, other: table_types):
        """Apply a union expression to this table expression.

        Union works like a vertical concatenation of two tables that is then filtered for duplicate rows.

        Args:
            other (Union[SelectTableExpression, WhereTableExpression, GroupByAggregation, RowSetOp]): the other
            table expression to take the union with.

        Returns:
            RowSetOp: RowSetOp instance representing the union of two table expressions.

        """
        return RowSetOp("union", self, other)

    def union_all(self, other: table_types):
        """Apply a union all expression to this table expression.

        Union works like a vertical concatenation of two tables that keeps duplicate rows.

        Args:
            other (Union[SelectTableExpression, WhereTableExpression, GroupByAggregation, RowSetOp]): the other
            table expression to take the union all with.

        Returns:
            RowSetOp: RowSetOp instance representing the union all of two table expressions.

        """
        return RowSetOp("union all", self, other)

    def intersect(self, other: table_types):
        """Apply an intersect expression to this table expression.

        Intersect returns the set of rows that are found in to input tables.

        Args:
            other (Union[SelectTableExpression, WhereTableExpression, GroupByAggregation, RowSetOp]): the other
            table expression to take the intersection with.

        Returns:
            RowSetOp: RowSetOp instance representing the intersection of two table expressions.

        """
        return RowSetOp("intersect", self, other)

    def exclude(self, other: table_types):
        """Apply an except (aka exclude in lumipy) expression to this table expression.

        Except takes two tables and returns the set of rows that are found in the first table but not the second.

        Args:
            other (Union[SelectTableExpression, WhereTableExpression, GroupByAggregation, RowSetOp]): the other
            table expression to take the except operation with.

        Returns:
            RowSetOp: RowSetOp instance representing the except of two table expressions.

        """
        return RowSetOp("except", self, other)
