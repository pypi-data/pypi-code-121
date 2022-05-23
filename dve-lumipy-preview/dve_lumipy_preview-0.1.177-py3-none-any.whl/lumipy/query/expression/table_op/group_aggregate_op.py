from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.query.expression.table_op.group_by_op import GroupBy
from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn


class GroupByAggregation(BaseTableExpression):
    """Class representing the aggregation part of a group by + aggregation on a table.

    """

    def __init__(self, group_by: GroupBy, **aggregates: BaseAggregateColumn):
        """__init__ method of the GroupbyAggregation class.

        All aggregate inputs must be as keyword args where the keyword is the alias to apply to the column aggregate.
        For example __init__([GroupBy], MeanDuration=table.duration.mean())

        Args:
            group_by (GroupBy): group by expression to apply aggregaton to.
            **aggregates (BaseAggregateColumn): keyword args where the values are all column aggregate expressions.
        """
        from .group_by_op import GroupBy
        if type(group_by) != GroupBy:
            raise TypeError(
                f"Aggregate expression must be given a groupby to aggregate. Was {type(group_by).__name__}."
            )

        self._group_by = group_by

        source = group_by.get_source_table()
        self._group_columns = group_by.get_group_columns()
        self._select_columns = group_by.get_select_columns()

        aliases = []
        aggregate_columns = []
        for k, v in aggregates.items():
            aliases.append(k)
            aggregate_columns.append(v)
        processed_aggregates = source.validate_source_columns(aggregate_columns)

        self._agg_columns = [c.with_alias(alias) for alias, c in zip(aliases, processed_aggregates)]

        super().__init__(
            self._select_columns + self._agg_columns,
            source.get_client(),
            'group aggregation',
            group_by.get_select_type(),
            group_by.get_source_table(),
            group_by,
            *self._agg_columns
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

        # Handle where clause conditions from parent
        from .where_op import WhereTableExpression
        where_strings = [p.get_sql() for p in self.get_source_table().get_parameters().values()]
        if type(self._group_by.get_parent()) == WhereTableExpression:
            where_strings.append(f"({self._group_by.get_parent().get_condition().get_sql()})")

        if len(where_strings) > 0:
            conditions = '\n  AND '.join(where_strings)
            out_str += f"\nWHERE\n  {conditions}"

        # Add group by clause
        out_str += f"\nGROUP BY\n  {', '.join(c.get_sql() for c in self._group_columns)}"

        return out_str

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

    def having(self, condition) -> 'HavingTableExpression':
        """Apply a having expression to this groupby/aggregate expression given a condition.

        The having SQL expression filters the groups according to the supplied condition. Rows that evaluate
        to False are not returned. Works just like a where statement.

        Args:
            condition (BaseColumnExpression): a column expression that resolves to a boolean SQL value type.

        Returns:
            HavingTableExpression: instance of WhereTableExpression representing the having clause applied to this
            group by aggregation table expression.

        """
        from .having_op import HavingTableExpression
        return HavingTableExpression(self, condition)

    filter = having

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
