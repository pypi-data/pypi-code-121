from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp
from lumipy.query.expression.column_op.common import get_expr_sql
from lumipy.query.expression.sql_value_type import numerics, SqlValType, fixed_type, all_types
from lumipy.query.expression.column.column_base import BaseColumnExpression


class Not(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Not, self).__init__(
            "not",
            lambda x: f"NOT {get_expr_sql(x)}",
            lambda x: x == SqlValType.Boolean,
            fixed_type(SqlValType.Boolean),
            value
        )


class IsNull(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(IsNull, self).__init__(
            "is null",
            lambda x: f"{get_expr_sql(x)} IS NULL",
            lambda x: x in all_types,
            fixed_type(SqlValType.Boolean),
            value
        )


class IsNotNull(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(IsNotNull, self).__init__(
            "is null",
            lambda x: f"{get_expr_sql(x)} IS NOT NULL",
            lambda x: x in all_types,
            fixed_type(SqlValType.Boolean),
            value
        )


class Negative(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Negative, self).__init__(
            "negative",
            lambda x: f"-{get_expr_sql(x)}",
            lambda x: x in numerics,
            lambda x: x,
            value
        )


class LowerCase(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(LowerCase, self).__init__(
            "lower case",
            lambda x: f"Lower({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Text,
            value
        )


class UpperCase(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(UpperCase, self).__init__(
            "upper case",
            lambda x: f"Upper({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Text,
            value
        )


class LogE(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(LogE, self).__init__(
            "natural log",
            lambda x: f"log({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            value
        )


class Log10(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Log10, self).__init__(
            "log base 10",
            lambda x: f"log10({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            value
        )


class Exp(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Exp, self).__init__(
            "exp",
            lambda x: f"exp({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            value
        )


class Ceil(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Ceil, self).__init__(
            "ceil",
            lambda x: f"ceil({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Int,
            value
        )


class Floor(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Floor, self).__init__(
            "floor",
            lambda x: f"floor({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Int,
            value
        )


class Abs(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Abs, self).__init__(
            "abs",
            lambda x: f"abs({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: x,
            value
        )


class Len(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Len, self).__init__(
            "string len",
            lambda x: f"length({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Int,
            value
        )


class Soundex(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Soundex, self).__init__(
            "soundex",
            lambda x: f"soundex({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Text,
            value
        )


class Unicode(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Unicode, self).__init__(
            "unicode",
            lambda x: f"unicode({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Int,
            value
        )


class Reverse(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Reverse, self).__init__(
            "reverse",
            lambda x: f"reverse({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Text,
            value
        )


class Proper(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Proper, self).__init__(
            "proper",
            lambda x: f"proper({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.Text,
            value
        )


class Sign(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(Sign, self).__init__(
            "sign",
            lambda x: f"sign({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Int,
            value
        )


class ToDate(BaseScalarOp):
    def __init__(self, value: BaseColumnExpression):
        super(ToDate, self).__init__(
            "to date",
            lambda x: f"To_Date({x.get_sql()})",
            lambda x: x == SqlValType.Text,
            lambda x: SqlValType.DateTime,
            value
        )
