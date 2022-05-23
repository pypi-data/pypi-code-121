from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.query.expression.column.column_literal import LiteralColumn


class LimitTableExpression(BaseTableExpression):
    """Class representing a limit expression on a table expression.

    """

    def __init__(self, parent: BaseTableExpression, limit: int):
        """__init__ method of the LimitTableExpression class.

        Args:
            parent (BaseTableExpression): table expression to apply the limit expression to.
            limit (int): value to limit by. Must be an int > 0.
        """

        if type(limit) != int:
            raise TypeError(f"Limit only accepts int values. Was {type(limit).__name__}")
        if limit < 1:
            raise ValueError(f"Limit value must be non-zero and positive. Was {limit}.")

        self._limit = limit
        super().__init__(
            parent.get_columns(),
            parent.get_client(),
            'limit',
            parent.get_select_type(),
            parent.get_source_table(),
            parent,
            LiteralColumn(limit)  # So it shows up in the DAG
        )

    def get_table_sql(self):
        """Get the SQL string for the table expression only. Not including the @/@@ var assignments.

        Returns:
            str: the table SQL string.
        """
        return f"{self._parent.get_table_sql()}" \
               f"\nLIMIT\n" \
               f"  {self._limit}"
