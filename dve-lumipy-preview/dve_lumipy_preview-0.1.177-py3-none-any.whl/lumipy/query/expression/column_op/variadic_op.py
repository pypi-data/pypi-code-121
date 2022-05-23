from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp
from lumipy.query.expression.sql_value_type import column_types


class Coalesce(BaseScalarOp):
    def __init__(self, *values: BaseColumnExpression):

        if len(values) < 2:
            raise ValueError(f"Coalesce expression must be given at least two values! Received {len(values)}.")

        super(Coalesce, self).__init__(
            "coalesce",
            lambda *args: f"coalesce({', '.join(a.get_sql() for a in args)})",
            lambda *args: all(a == args[0] for a in args) and args[0] in column_types,
            lambda *args: args[0],
            *values
        )
