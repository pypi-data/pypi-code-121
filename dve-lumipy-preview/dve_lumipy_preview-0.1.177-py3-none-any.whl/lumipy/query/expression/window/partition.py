from ..base_sql_expression import BaseSqlExpression
from ..column.column_base import BaseColumnExpression
from ..sql_value_type import SqlValType


class WindowPartition(BaseSqlExpression):
    """Class that represents the partition part of an OVER clause in a SQL window function.

    """

    def __init__(self, *columns: BaseColumnExpression):
        """Constructor for the WindowPartition class.

        Args:
            *columns (BaseColumnExpression): column expressions that define the window partition.
        """

        if any(not isinstance(c, BaseColumnExpression) for c in columns):
            raise TypeError("Args to WindowPartition constructor must be subclasses of BaseColumnExpression.")

        if len(columns) == 0:
            raise ValueError("Must supply atleast one column expression object. Received zero.")

        self.groups = columns

        super().__init__(
            "window partition",
            lambda *args: f"PARTITION BY {', '.join(a.get_sql() for a in args)}",
            lambda *args: True,
            lambda *args: SqlValType.ColumnSelection,
            *columns
        )

