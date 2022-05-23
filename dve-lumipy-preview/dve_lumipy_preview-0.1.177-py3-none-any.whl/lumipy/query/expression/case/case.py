from ..base_sql_expression import BaseSqlExpression
from ..column.column_base import BaseColumnExpression
from ..column.column_literal import python_to_expression
from ..sql_value_type import SqlValType, column_types


class CaseStart(BaseSqlExpression):

    def __init__(self, source_hash):

        self._source_hash = python_to_expression(source_hash)

        super().__init__(
            "case start",
            lambda x: f"  CASE",
            lambda x: True,
            lambda x: SqlValType.Unit,
            self._source_hash
        )

    def get_source_hash(self):
        return self._source_hash

    def when(self, condition):
        from .when import When
        return When(self, condition)


class CaseEnd(BaseColumnExpression):

    def __init__(self, then, value):

        in_value = python_to_expression(value)
        if not isinstance(in_value, BaseColumnExpression):
            raise TypeError(f"Input value to .otherwise() must be a column expression. Was {type(value).__name__}.")

        super().__init__(
            then.get_source_hash().get_py_value(),
            lambda x, y: f"(  \n{x.get_sql()}\n    ELSE {y.get_sql()}\n  END\n)",
            lambda x, y: y in column_types + [SqlValType.Null],
            lambda x, y: y if y != SqlValType.Null else then.get_type(),
            'case else',
            then,
            in_value
        )
