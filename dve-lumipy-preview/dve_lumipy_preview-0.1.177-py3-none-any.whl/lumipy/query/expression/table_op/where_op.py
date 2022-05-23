from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.query.expression.sql_value_type import SqlValType
from .select_op import SelectTableExpression


class WhereTableExpression(BaseTableExpression):
    """Class representing a where statement on a source table select statement.

    """

    def __init__(self, parent: SelectTableExpression, condition: BaseColumnExpression):
        """__init__ method of the WhereTableExpression class.

        Args:
            parent (SelectTableExpression): parent select table expression.
            condition (BaseColumnExpression): condition that this where expression applies to the select.
        """
        if type(parent) != SelectTableExpression:
            raise TypeError(
                f"Where expression must be built with a SelectTableExpression parent. Was {type(parent).__name__}."
            )
        if not issubclass(type(condition), BaseColumnExpression):
            raise TypeError(
                f"Where condition must be a column expression type. Was {type(condition).__name__}."
            )
        if condition.get_type() != SqlValType.Boolean:
            raise TypeError(
                f"Where condition expression does not resolve to a boolean. Was {condition.get_type()}."
            )

        # validate and modify where condition expression according to source table
        # SourceTable will check for membership, join tables will add prefixes and handle duplicate aliasing
        self._condition = parent.get_source_table().validate_source_columns([condition])[0]

        super().__init__(
            parent.get_columns(),
            parent.get_client(),
            'where',
            parent.get_select_type(),
            parent.get_source_table(),
            parent,
            condition
        )

    def get_condition(self) -> BaseColumnExpression:
        """Get the condition expression that defines this where expression.

        Returns:
            BaseColumnExpression: the condition expression.
        """
        return self._condition

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
        where_strings.append(f"({self._condition.get_sql()})")
        conditions = '\n  AND '.join(where_strings)
        out_str += f"\nWHERE\n  {conditions}"
        return out_str

    def group_by(self, *columns):
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

    def order_by(self, *order_bys):
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

    def limit(self, limit):
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

    def union(self, other):
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

    def union_all(self, other):
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
