from datetime import date, datetime
from typing import Union

from lumipy.query.expression.column.column_alias import AliasedColumn
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_ordering import BaseColumnOrdering
from lumipy.query.expression.column.column_prefix import PrefixedColumn
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.table.base_source_table import SourceTable
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.query.expression.column.column_literal import python_to_expression


def _valid_args(args):
    ok_types = [SourceColumn, PrefixedColumn, AliasedColumn]
    if not all(any(isinstance(c, t) for t in ok_types) for c in args):
        raise TypeError(
            f"Only source columns can be supplied as unnamed args. Other columns types such"
            f" as functions of columns or literals must be supplied as keyword args (except '*' and '^').\n"
            " ⮕Try something like one of the following:\n"
            "   •Scalar functions of columns: \n"
            "      provider.select(col_doubled=provider.col*2)\n"
            "   •Aggregate functions of columns: \n"
            "      provider.select(col_sum=provider.col.sum())\n"
            "   •Python literals: \n"
            "      provider.select(higgs_mass=125.1)\n"
        )


class SelectTableExpression(BaseTableExpression):
    """Class representing a select statement on a source table.

    """

    def __init__(
            self,
            source_table: SourceTable,
            distinct: bool,
            *cols: Union[SourceColumn, PrefixedColumn, AliasedColumn],
            **aliased_cols: BaseColumnExpression
    ):
        """__init__ method of the SelectTableExpression class.

        Args:
            source_table (SourceTable): the source table the select is to be applied to.
            distinct (bool): whether the select statement is 'select' (False) or 'select distinct' True.
            *cols (Union[SourceColumn, PrefixedColumn, AliasedColumn]): the column expressions that are
            selected by the select statement. Can be only be source column, aliased/prefixed source column.
            **aliased_cols (Union[BaseColumnExpression, str, int, float, date, datetime, bool]): column expression to
            select with an alias. The keyword is the alias and the value will be what the alias is applied to.
        """

        if not issubclass(type(source_table), SourceTable):
            raise TypeError(f"SelectTable must be given a source table type. Was {type(source_table).__name__}.")

        if len(cols) == 0 and len(aliased_cols) == 0:
            raise ValueError('No columns supplied to the select')

        cols = source_table.handle_star_or_caret(cols)
        _valid_args(cols)

        aliases = [python_to_expression(c).with_alias(a) for a, c in aliased_cols.items()]

        self._distinct = distinct
        select_str = 'select'
        if self._distinct:
            select_str += ' distinct'

        columns = list(cols)+aliases

        super().__init__(
            columns,
            source_table.get_client(),
            select_str,
            select_str,
            source_table,
            source_table,
            *columns
        )

    def get_table_sql(self) -> str:
        """Get the SQL string for the table expression only. Not including the @/@@ var assignments.

        Returns:
            str: the table SQL string.
        """
        cols_str = ", ".join(c.get_sql() for c in self.get_columns())
        out_str = f"{self.get_select_type().upper()}\n  {cols_str}\n" \
                  f"FROM\n" \
                  f"  {self.get_source_table().get_from_arg_string()}"
        where_strings = [p.get_sql() for p in self.get_source_table().get_parameters().values()]
        if len(where_strings) > 0:
            conditions = '\n  AND '.join(where_strings)
            out_str += f"\nWHERE\n  {conditions}"
        return out_str

    # noinspection PyUnresolvedReferences
    def where(self, condition: BaseColumnExpression) -> 'WhereTableExpression':
        """Apply a where expression to this table expression given a condition.

        The where SQL expression filters the selected rows according to the supplied condition. Rows that evaluate
        to False are not returned.

        Args:
            condition (BaseColumnExpression): a column expression that resolves to a boolean SQL value type.

        Returns:
            WhereTableExpression: instance of WhereTableExpression representing the where clause applied to this select
            statement.
        """
        from .where_op import WhereTableExpression
        return WhereTableExpression(self, condition)

    filter = where

    # noinspection PyUnresolvedReferences
    def group_by(self, *columns: BaseColumnExpression) -> 'GroupBy':
        """Apply a group by expression to this table expression given a collection of column expressions.

        This corresponds to one part of thr group by syntax and doesn't resolve to any SQL. Call aggregate() on the
        result of this method to define the group aggregates.

        Args:
            *columns BaseColumnExpression: column expressions to group by.

        Returns:
            GroupBy: GroupBy instance representing the group by statement applied to this expression.
        """
        from .group_by_op import GroupBy
        return GroupBy(self, *columns)

    # noinspection PyUnresolvedReferences
    def order_by(self, *order_bys: BaseColumnOrdering) -> 'OrderedTableExpression':
        """Apply an order by expression to this table expression given a collection of column ordering expressions.

        Sort a table's rows according to a collection of columns/functions of columns.

        Args:
            *order_bys:column ordering expression args in teh order they are to be applied.

        Returns:
            OrderedTableExpression: OrderedTableExpression instance representing the ordering applied to this table
            expression.
        """
        from .order_by_op import OrderedTableExpression
        return OrderedTableExpression(self, *order_bys)

    # noinspection PyUnresolvedReferences
    def limit(self, limit: int) -> 'LimitTableExpression':
        """Apply a limit expression to this table.

        Limit will take the first n-many rows of the table.

        Args:
            limit (int): the limit value

        Returns:
            LimitTableExpression: LimitTableExpression instance representing the limit expression applied to this table
            expression.
        """
        from .limit_op import LimitTableExpression
        return LimitTableExpression(self, limit)

    # noinspection PyUnresolvedReferences
    def union(self, other: BaseTableExpression) -> 'RowSetOp':
        """Apply a union expression to this table.

        Union works like a vertical concatenation of two table expressions that is then filtered for distinct rows.

        Args:
            other (BaseTableExpression): the other table expression to take the 'union' with.

        Returns:
            RowSetOp: a RowSetOp instance representing the union between this table expression and the
            argument table expression.

        """
        from .row_set_op import RowSetOp
        return RowSetOp("union", self, other)

    # noinspection PyUnresolvedReferences
    def union_all(self, other: BaseTableExpression) -> 'RowSetOp':
        """Apply a union all expressinon to this table.

        Union all works like a vertical concatenation of two tables. Unlike 'union' it doesn't filter duplicates rows
        out. The number of columns between the two table expressions must match.

        Args:
            other (BaseTableExpression): the other table expression to take the 'union all' with.

        Returns:
            RowSetOp: a RowSetOp instance representing the union all between this table expression and the
            argument table expression.

        """
        from .row_set_op import RowSetOp
        return RowSetOp("union all", self, other)

    def intersect(self, other):
        """Apply an intersect expression to this table expression.

        Intersect returns the set of rows that are found in to input tables.

        Args:
            other (Union[SelectTableExpression, WhereTableExpression, GroupByAggregation, RowSetOp]): the other
            table expression to take the intersection with.

        Returns:
            RowSetOp: RowSetOp instance representing the intersection of two table expressions.

        """
        from .row_set_op import RowSetOp
        return RowSetOp("intersect", self, other)

    def exclude(self, other):
        """Apply an except (aka exclude in lumipy) expression to this table expression.

        Except takes two tables and returns the set of rows that are found in the first table but not the second.

        Args:
            other (Union[SelectTableExpression, WhereTableExpression, GroupByAggregation, RowSetOp]): the other
            table expression to take the except operation with.

        Returns:
            RowSetOp: RowSetOp instance representing the except of two table expressions.

        """
        from .row_set_op import RowSetOp
        return RowSetOp("except", self, other)
