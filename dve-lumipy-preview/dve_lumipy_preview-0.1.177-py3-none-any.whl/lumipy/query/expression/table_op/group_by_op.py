from typing import List

from lumipy.query.expression.base_expression import BaseExpression
from lumipy.query.expression.column.column_alias import AliasedColumn
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import LiteralColumn, python_to_expression
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn
from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression


class GroupBy(BaseExpression):
    """Class representing the grouping part of a group by + aggregation on a table.

    """

    def __init__(self, parent: BaseTableExpression, *group_by_columns: BaseColumnExpression):
        """__init__ method of the GroupBy class.

        Args:
            parent (BaseTableExpression): table expression to apply grouping expression to.
            *group_by_columns (BaseColumnExpression): column expressions to be used to define the groups.
        """

        if any(isinstance(python_to_expression(g), LiteralColumn) for g in group_by_columns):
            raise TypeError(
                "Literals are not allowed in group_by(). Please supply them in select() as a keyword argument."
            )

        # Unwrap aliased columns (happens when there's an auto-aliased column attribute on a join table object
        group_by_columns = [gc.get_original() if isinstance(gc, AliasedColumn) else gc for gc in group_by_columns]

        self._client = parent.get_client()
        self._source_table = parent.get_source_table()

        select_hashes = [hash(c) for c in parent.get_columns()]
        select_hashes += [hash(c.get_original()) for c in parent.get_columns() if isinstance(c, AliasedColumn)]

        group_by_cols = parent.get_source_table().validate_source_columns(group_by_columns)
        self._group_by_cols = [c.get_original() if isinstance(c, AliasedColumn) else c for c in group_by_cols]

        self._selected_columns = parent.get_columns()
        self._selected_columns += [c for c in self._group_by_cols if hash(c) not in select_hashes and isinstance(c, SourceColumn)]

        self._select_type = parent.get_select_type()
        self._parent_table = parent

        in_values = [parent] + self._group_by_cols
        super().__init__(
            "group by",
            lambda *args: True,
            lambda *args: SqlValType.Grouping,
            *in_values
        )

    def get_select_type(self):
        """Get the select type string ('select' or 'select distinct')

        Returns:
            str: the select type
        """
        return self._select_type

    def aggregate(self, *args: BaseAggregateColumn, **kwargs: BaseAggregateColumn) -> 'GroupByAggregation':
        """Apply a collection of aggregations to the group by expression.

        All inputs must be as keyword args where the keyword is the alias to apply to the column aggregate.
        For example .aggregate(MeanDuration=table.duration.mean())

        Args:
            **kwargs (BaseAggregateColumn): keyword args where the values are all column aggregate expressions.

        Returns:
            GroupByAggregation: GroupByAggregation instance representing aggregates over groups in this group by
            expression.
        """
        from .group_aggregate_op import GroupByAggregation
        if len(args) > 0:
            raise ValueError(
                "Aggregate method only takes keyword arguments "
                "(For example: MeanValue=table.column.mean())"
            )
        return GroupByAggregation(self, **kwargs)

    def get_source_table(self) -> 'BaseSourceTable':
        """Get the source table expression object that this table expression depends on.

        Returns:
            BaseSourceTable: the source table of this table expression.
        """
        return self._source_table

    def get_group_columns(self) -> List[BaseColumnExpression]:
        """Get the column expressions that define the group by.

        Returns:
            List[BaseColumnExpression]: list of the group by columns.
        """
        return self._group_by_cols

    def get_select_columns(self):
        """Get the column expressions that define the group by.

        Returns:
            List[BaseColumnExpression]: list of the group by columns.
        """
        return self._selected_columns

    def get_parent(self) -> BaseExpression:
        """Get the parent expression this expression was chained from.

        Returns:
            BaseExpression: the parent expression.
        """
        return self._parent_table
