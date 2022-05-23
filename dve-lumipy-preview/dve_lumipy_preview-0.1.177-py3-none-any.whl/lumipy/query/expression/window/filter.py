from ..base_sql_expression import BaseSqlExpression
from ..sql_value_type import SqlValType


class WindowFilter(BaseSqlExpression):

    def __init__(self, expression):

        self._filter_expr = expression

        super().__init__(
            "window filter",
            lambda x: f"FILTER(WHERE {x.get_sql()})",
            lambda x: x == SqlValType.Boolean,
            lambda x: SqlValType.ColumnSelection,
            expression
        )

    def get_expression(self):
        return self._filter_expr
