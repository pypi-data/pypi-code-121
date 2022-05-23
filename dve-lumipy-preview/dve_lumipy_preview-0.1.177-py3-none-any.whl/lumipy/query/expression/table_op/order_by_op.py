from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from ..column.column_ordering import BaseColumnOrdering
from typing import List


class OrderedTableExpression(BaseTableExpression):
    """Class representing an order by expression applied data selected from a table.

    """

    def __init__(self, parent: BaseTableExpression, *orderings: BaseColumnOrdering):
        """__init__ method of the OrderedTableExpression class.

        Args:
            parent (BaseTableExpression): the parent table expression to apply order by to.
            *orderings (BaseColumnOrdering): ordering expressions defining the column orderings to apply.
        """
        if len(orderings) == 0:
            raise ValueError("OrderedTableExpression received empty input. Nothing to order by.")

        if any(not issubclass(type(o), BaseColumnOrdering) for o in orderings):
            raise TypeError(
                f"OrderBy received input that wasn't an ordering. Try using the ascending() "
                f"or descending() methods on a column object."
            )

        self._orderings = []

        # Special logic because orderings are not column types
        ord_types = [type(o) for o in orderings]
        insides = [o.get_ordering_column() for o in orderings]
        prepros = parent.get_source_table().validate_source_columns(insides)
        self._orderings = [ord_type(col) for ord_type, col in zip(ord_types, prepros)]

        super().__init__(
            parent.get_columns(),
            parent.get_client(),
            'order by',
            parent.get_select_type(),
            parent.get_source_table(),
            parent,
            *orderings
        )

    def get_orderings(self) -> List[BaseColumnOrdering]:
        """Get a list of the ordering expressions that define this order by expression

        Returns:
            List[BaseColumnOrdering]: the list of ordering expressions.
        """
        return self._orderings

    def get_table_sql(self):
        """Get the SQL string for the table expression only. Not including the @/@@ var assignments.

        Returns:
            str: the table SQL string.
        """
        orders = ", ".join(o.get_sql() for o in self._orderings)
        return f"{self._parent.get_table_sql()}" \
               f"\nORDER BY\n" \
               f"  {orders}"

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
