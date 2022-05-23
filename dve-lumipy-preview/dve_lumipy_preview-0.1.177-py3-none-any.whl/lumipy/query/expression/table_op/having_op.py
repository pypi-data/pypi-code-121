from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.query.expression.base_expression import BaseExpression
from .group_aggregate_op import GroupByAggregation
from lumipy.query.expression.column.column_base import BaseColumnExpression


class HavingTableExpression(BaseTableExpression):
    """Class representing a having statement on a group by aggregation.

    """

    def __init__(self, parent: GroupByAggregation, condition: BaseColumnExpression):
        """__init__ method of the HavingTableExpression class.

        Args:
            parent (GroupByAggregation): parent group by aggregation expression.
            condition (BaseColumnExpression): condition column expression that this having statement applies.
        """

        # Must be an aggregated group by
        if type(parent) != GroupByAggregation:
            raise TypeError(
                f"Having expression must be built with GroupByAggregation parent. Was {type(parent).__name__}."
            )
        if not issubclass(type(condition), BaseExpression):
            raise TypeError(
                f"Having condition must be an expression type. Was {type(condition).__name__}."
            )
        if condition.get_type() != SqlValType.Boolean:
            raise TypeError(
                f"Having condition expression does not resolve to a boolean. Was {condition.get_type()}."
            )

        self._parent = parent
        self._condition = parent.get_source_table().validate_source_columns([condition])[0]

        super().__init__(
            parent.get_columns(),
            parent.get_client(),
            'having',
            parent.get_select_type(),
            parent.get_source_table(),
            parent,
            condition
        )

    def get_condition(self):
        """Get the condition expression that defines this having expression.

        Returns:
            BaseColumnExpression: the condition expression.
        """
        return self._condition

    def get_table_sql(self):
        """Get the SQL string for the table expression only. Not including the @/@@ var assignments.

        Returns:
            str: the table SQL string.
        """
        return f"{self._parent.get_table_sql()}" \
               f"\nHAVING\n" \
               f"  {self._condition.get_sql()}"

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
