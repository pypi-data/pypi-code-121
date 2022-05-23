from lumipy.query.expression.base_sql_expression import BaseSqlExpression
from lumipy.query.expression.sql_value_type import SqlValType, column_types
from ..column.column_base import BaseColumnExpression
from ..column.column_literal import python_to_expression


class Then(BaseSqlExpression):

    def __init__(self, when, value):

        self._source_hash = when.get_source_hash()

        self._value = python_to_expression(value)
        self._when = when

        if not isinstance(self._value, BaseColumnExpression):
            raise TypeError(f"Input value to .then() must be a column expression. Was {type(value).__name__}.")

        super().__init__(
            'then',
            lambda x, y: f"{x.get_sql()}\n        THEN {y.get_sql()}",
            lambda x, y: y in column_types,
            lambda x, y: y,
            self._when,
            self._value
        )

    def get_source_hash(self):
        return self._source_hash

    def when(self, condition):
        """Create a new WHEN condition and add it to the case expression chain.

        Args:
            condition (BaseColumnExpression): when condition to add, must be a column expression that resolves to a
            boolean.

        Returns:
            When: the When object representing the new WHEN clause added to the case expression chain.
        """
        from .when import When
        return When(self, condition)

    def otherwise(self, value=None):
        """Add the final clause to the case expression chain. This is the ELSE equivalent.

        Args:
            value: Optional value to associate with the ELSE condition. Can be column expression or a python literal.
            If no value is supplied this is equivalent to the else case being null.

        Returns:
            CaseEnd: the CaseEnd object representing the end of the case expression.
        """
        from .case import CaseEnd
        return CaseEnd(self, value)
