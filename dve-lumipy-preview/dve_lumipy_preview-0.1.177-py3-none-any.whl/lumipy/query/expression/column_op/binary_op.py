from lumipy.query.expression.column_op.common import get_expr_sql
from lumipy.query.expression.sql_value_type import numerics, numeric_priority, \
    SqlValType, fixed_type, \
    comparables
from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp
from lumipy.query.expression.column.column_base import BaseColumnExpression
from typing import Union


class Add(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "add",
            lambda x, y: f"{get_expr_sql(x)} + {get_expr_sql(y)}",
            lambda x, y: x in numerics and y in numerics,
            numeric_priority,
            value1,
            value2
        )


class Sub(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "subtract",
            lambda x, y: f"{get_expr_sql(x)} - {get_expr_sql(y)}",
            lambda x, y: x in numerics and y in numerics,
            numeric_priority,
            value1,
            value2
        )


class Strftime(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):

        fmt = unwrap_if_literal(value1)
        if isinstance(fmt, str) and value1 == '%s':
            out_type = SqlValType.BigInt
        else:
            out_type = SqlValType.Text

        super().__init__(
            "strftime",
            lambda x, y: f"strftime({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x == SqlValType.Text and y in {SqlValType.DateTime, SqlValType.Date},
            lambda x, y: out_type,
            value1,
            value2
        )


class Mul(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "multiply",
            lambda x, y: f"{get_expr_sql(x)} * {get_expr_sql(y)}",
            lambda x, y: x in numerics and y in numerics,
            numeric_priority,
            value1,
            value2
        )


class Div(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "divide",
            lambda x, y: f"{get_expr_sql(x)} / {get_expr_sql(y)}",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: y,
            value1,
            value2
        )


class Mod(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "modulus",
            lambda x, y: f"{get_expr_sql(x)} % {get_expr_sql(y)}",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Int,
            value1,
            value2
        )


class BitwiseAnd(BaseScalarOp):
    # Todo: type checking is incorrect. Not boolean inputs.
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "bitwise and",
            lambda x, y: f"{get_expr_sql(x)} & {get_expr_sql(y)}",
            lambda x, y: x == SqlValType.Boolean and y == SqlValType.Boolean,
            lambda x, y: SqlValType.Boolean,
            value1,
            value2
        )


class BitwiseOr(BaseScalarOp):
    # Todo: type checking is incorrect. Not boolean inputs.
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "bitwise or",
            lambda x, y: f"{get_expr_sql(x)} | {get_expr_sql(y)}",
            lambda x, y: x == SqlValType.Boolean and y == SqlValType.Boolean,
            lambda x, y: SqlValType.Boolean,
            value1,
            value2
        )


class BitwiseXor(BaseScalarOp):
    # Todo: type checking is incorrect. Not boolean inputs.
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "bitwise xor",
            lambda x, y: f"{get_expr_sql(x)} ^ {get_expr_sql(y)}",
            lambda x, y: x == SqlValType.Boolean and y == SqlValType.Boolean,
            lambda x, y: SqlValType.Boolean,
            value1,
            value2
        )


class StringConcat(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "string concat",
            lambda x, y: f"{get_expr_sql(x)} || {get_expr_sql(y)}",
            lambda x, y: x == SqlValType.Text and y == SqlValType.Text,
            fixed_type(SqlValType.Text),
            value1,
            value2
        )


class Equals(BaseScalarOp):
    # todo: change comparables -> equatable
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "equal",
            lambda x, y: f"{get_expr_sql(x)} = {get_expr_sql(y)}",
            lambda x, y: {x, y} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class NotEquals(BaseScalarOp):
    # todo: change comparables -> equatable
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "not equal",
            lambda x, y: f"{get_expr_sql(x)} != {get_expr_sql(y)}",
            lambda x, y: {x, y} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class GreaterThan(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "greater than",
            lambda x, y: f"{get_expr_sql(x)} > {get_expr_sql(y)}",
            lambda x, y: {x, y} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class LessThan(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "less than",
            lambda x, y: f"{get_expr_sql(x)} < {get_expr_sql(y)}",
            lambda x, y: {x, y} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class GreaterThanOrEqual(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "greater or equal",
            lambda x, y: f"{get_expr_sql(x)} >= {get_expr_sql(y)}",
            lambda x, y: {x, y} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class LessThanOrEqual(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super().__init__(
            "less or equal",
            lambda x, y: f"{get_expr_sql(x)} <= {get_expr_sql(y)}",
            lambda x, y: {x, y} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class And(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(And, self).__init__(
            "and",
            lambda x, y: f"{get_expr_sql(x)} AND {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Boolean},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class Or(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Or, self).__init__(
            "or",
            lambda x, y: f"{get_expr_sql(x)} OR {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Boolean},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class IsIn(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):

        from lumipy.query.expression.column.collection import CollectionExpression
        if not isinstance(value2, CollectionExpression):
            raise TypeError("Second arg to IN/NOT IN expression must be a CollectionExpression.")

        super(IsIn, self).__init__(
            "is in",
            lambda x, y: f"{get_expr_sql(x)} IN {y.get_sql()}",
            lambda x, y: True,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class NotIn(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):

        from lumipy.query.expression.column.collection import CollectionExpression
        if not isinstance(value2, CollectionExpression):
            raise TypeError("Second arg to IN/NOT IN expression must be a CollectionExpression.")

        super(NotIn, self).__init__(
            "is not in",
            lambda x, y: f"{get_expr_sql(x)} NOT IN {y.get_sql()}",
            lambda x, y: True,
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class Like(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Like, self).__init__(
            "like",
            lambda x, y: f"{get_expr_sql(x)} LIKE {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Text},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class NotLike(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(NotLike, self).__init__(
            "not like",
            lambda x, y: f"{get_expr_sql(x)} NOT LIKE {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Text},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class Glob(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Glob, self).__init__(
            "glob",
            lambda x, y: f"{get_expr_sql(x)} GLOB {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Text},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class NotGlob(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(NotGlob, self).__init__(
            "not glob",
            lambda x, y: f"{get_expr_sql(x)} NOT GLOB {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Text},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class Regexp(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Regexp, self).__init__(
            "regexp",
            lambda x, y: f"{get_expr_sql(x)} REGEXP {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Text},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class NotRegexp(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(NotRegexp, self).__init__(
            "not regexp",
            lambda x, y: f"{get_expr_sql(x)} NOT REGEXP {get_expr_sql(y)}",
            lambda x, y: {x, y} == {SqlValType.Text},
            fixed_type(SqlValType.Boolean),
            value1,
            value2
        )


class Power(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Power, self).__init__(
            "power",
            lambda x, y: f"power({get_expr_sql(x)}, {get_expr_sql(y)})",
            lambda x, y: x in numerics and y in numerics,
            numeric_priority,
            value1,
            value2
        )


class Round(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Round, self).__init__(
            "round",
            lambda x, y: f"round({get_expr_sql(x)}, {get_expr_sql(y)})",
            lambda x, y: x in numerics and y == SqlValType.Int,
            lambda x, y: SqlValType.Double,
            value1,
            value2
        )


class CastTo(BaseScalarOp):
    def __init__(self, value, to_type):
        from lumipy.query.expression.column.column_literal import LiteralColumn

        if isinstance(to_type, LiteralColumn):
            to_type_str = to_type.get_py_value()
        else:
            to_type_str = to_type

        super(CastTo, self).__init__(
            f"cast to {to_type_str}",
            lambda x, y: f"cast({x.get_sql()} AS {to_type_str.upper()})",
            lambda x, y: True,
            lambda x, y: SqlValType[to_type_str],
            value,
            to_type,
        )


def unwrap_if_literal(val):
    from lumipy.query.expression.column.column_literal import LiteralColumn
    if isinstance(val, LiteralColumn):
        return val.get_py_value()
    else:
        return val


class Trim(BaseScalarOp):
    def __init__(
            self,
            value1: BaseColumnExpression,
            value2: BaseColumnExpression,
            trim_type: Union[str, BaseColumnExpression]
    ):

        trim_str = unwrap_if_literal(value2)

        trim_type_str = unwrap_if_literal(trim_type)

        if trim_str == '':
            expr_fn = lambda x, y, z: f"{trim_type_str}trim({x.get_sql()})"
        else:
            expr_fn = lambda x, y, z: f"{trim_type_str}trim({x.get_sql()}, {y.get_sql()})"

        super(Trim, self).__init__(
            f"{trim_type_str} trim",
            expr_fn,
            lambda x, y, z: x == SqlValType.Text and y == SqlValType.Text and z == SqlValType.Text,
            lambda x, y, z: SqlValType.Text,
            value1,
            value2,
            trim_type
        )


class Replicate(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(Replicate, self).__init__(
            "replicate",
            lambda x, y: f"replicate({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x == SqlValType.Text and y == SqlValType.Int,
            lambda x, y: SqlValType.Text,
            value1,
            value2
        )


class LeftStr(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(LeftStr, self).__init__(
            "left string",
            lambda x, y: f"leftstr({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x == SqlValType.Text and y == SqlValType.Int,
            lambda x, y: SqlValType.Text,
            value1,
            value2
        )


class RightStr(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression):
        super(RightStr, self).__init__(
            "right string",
            lambda x, y: f"rightstr({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x == SqlValType.Text and y == SqlValType.Int,
            lambda x, y: SqlValType.Text,
            value1,
            value2
        )


class Pad(BaseScalarOp):
    def __init__(
            self,
            value1: BaseColumnExpression,
            value2: Union[int, BaseColumnExpression],
            pad_type: Union[str, BaseColumnExpression]
    ):
        pad_type_str = unwrap_if_literal(pad_type)

        super(Pad, self).__init__(
            f"pad {pad_type_str}",
            lambda x, y, z: f"pad{pad_type_str}({x.get_sql()}, {y.get_sql()})",
            lambda x, y, z: x == SqlValType.Text and y == SqlValType.Int,
            lambda x, y, z: SqlValType.Text,
            value1,
            value2,
            pad_type
        )


class StrFilter(BaseScalarOp):
    def __init__(
            self,
            value1: Union[str, BaseColumnExpression],
            value2: Union[str, BaseColumnExpression]
    ):
        super(StrFilter, self).__init__(
            "string filter",
            lambda x, y: f"strfilter({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x == SqlValType.Text and y == SqlValType.Text,
            lambda x, y: SqlValType.Text,
            value1,
            value2
        )


class RandomUniformFloat(BaseScalarOp):
    def __init__(
            self,
            value1: Union[int, float, BaseColumnExpression],
            value2: Union[int, float, BaseColumnExpression],
    ):
        def random_uniform(x, y):
            """Generate random uniform sample sql

            This expression works by sampling with RANDOM, rescaling it to between 0 and 1, and then scaling (0, 1) to
            the user-specified range (x, y).

            Args:
                x: lower limit value
                y: upper limit value

            Returns:
                str: random uniform sampling SQL string.
            """
            return f"({y.get_sql()} - {x.get_sql()})*(0.5 - RANDOM() / CAST(-18446744073709551616 AS REAL)) + {x.get_sql()}"

        super(RandomUniformFloat, self).__init__(
            'random uniform float',
            random_uniform,
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            value1,
            value2
        )
