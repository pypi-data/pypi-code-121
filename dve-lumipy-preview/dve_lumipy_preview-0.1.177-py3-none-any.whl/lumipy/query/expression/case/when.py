from lumipy.query.expression.base_sql_expression import BaseSqlExpression
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.sql_value_type import SqlValType


class When(BaseSqlExpression):

    def __init__(self, then, condition):

        self._source_hash = then.get_source_hash()

        self._condition = condition
        self._then = then

        if not isinstance(condition, BaseColumnExpression) or condition.get_type() != SqlValType.Boolean:

            detail = f" Was an {type(condition).__name__} type"
            if isinstance(condition, BaseColumnExpression):
                detail += f" that resolves to {condition.get_type().name}"

            raise TypeError(
                "Condition input to .when() must be column expression that resolves to a boolean value."
                + detail + '.'
            )

        super().__init__(
            "when",
            lambda x, y: f"{x.get_sql()}\n      WHEN {y.get_sql()}",
            lambda x, y: y == SqlValType.Boolean,
            lambda x, y: SqlValType.Unit,
            self._then,
            self._condition
        )

    def get_source_hash(self):
        return self._source_hash

    def then(self, value):
        """Add a then clause to the case expression chain. THEN associates a value with the WHEN clause preceding it.

        Args:
            value: value to associate with the prior WHEN condition. Can be a column expression or python literal.

        Returns:
            Then: the Then object representing the then clause added to the chain.
        """
        from .then import Then
        return Then(self, value)
