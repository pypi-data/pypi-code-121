from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp
from lumipy.query.expression.column_op.common import get_expr_sql
from lumipy.query.expression.sql_value_type import SqlValType, fixed_type, comparables
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import python_to_expression
from typing import Union


class Between(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression, value3: BaseColumnExpression):

        value2 = python_to_expression(value2)
        value3 = python_to_expression(value3)

        if value2.get_py_value() >= value3.get_py_value():
            raise ValueError('Invalid interval given to BETWEEN. Upper limit must be greater than the lower limit.')

        super(Between, self).__init__(
            "between values",
            lambda x, y, z: f"{get_expr_sql(x)} BETWEEN {get_expr_sql(y)} AND {get_expr_sql(z)}",
            lambda x, y, z: {x, y} in comparables and {x, z} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2,
            value3
        )


class NotBetween(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression, value3: BaseColumnExpression):

        value2 = python_to_expression(value2)
        value3 = python_to_expression(value3)

        if value2.get_py_value() >= value3.get_py_value():
            raise ValueError('Invalid interval given to NOT BETWEEN. Upper limit must be greater than the lower limit.')

        super(NotBetween, self).__init__(
            "not between values",
            lambda x, y, z: f"{get_expr_sql(x)} NOT BETWEEN {get_expr_sql(y)} AND {get_expr_sql(z)}",
            lambda x, y, z: {x, y} in comparables and {x, z} in comparables,
            fixed_type(SqlValType.Boolean),
            value1,
            value2,
            value3
        )


class StrReplace(BaseScalarOp):
    def __init__(self, value1: BaseColumnExpression, value2: BaseColumnExpression, value3: BaseColumnExpression):
        super(StrReplace, self).__init__(
            "str replace",
            lambda x, y, z: f"Replace({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda *args: all(a == SqlValType.Text for a in args),
            fixed_type(SqlValType.Text),
            value1,
            value2,
            value3
        )


class Substr(BaseScalarOp):
    def __init__(
            self,
            value1: Union[str, BaseColumnExpression],
            value2: Union[int, BaseColumnExpression],
            value3: Union[int, BaseColumnExpression]
    ):
        super(Substr, self).__init__(
            'substr',
            lambda x, y, z: f"substr({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda x, y, z: x == SqlValType.Text and y == SqlValType.Int and z == SqlValType.Int,
            fixed_type(SqlValType.Text),
            value1,
            value2,
            value3
        )


class Index(BaseScalarOp):
    def __init__(
            self,
            value1: Union[str, BaseColumnExpression],
            value2: Union[str, BaseColumnExpression],
            value3: Union[int, BaseColumnExpression]
    ):
        super(Index, self).__init__(
            "char index",
            lambda x, y, z: f"charindex({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda x, y, z: x == SqlValType.Text and y == SqlValType.Text and z == SqlValType.Int,
            lambda x, y, z: SqlValType.Int,
            value1,
            value2,
            value3
        )
