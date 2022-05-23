from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.variable.base_variable import BaseVariable
from lumipy.query.expression.table_op.base_table_op import BaseTableExpression
from lumipy.common.string_utils import sql_str_to_name
from lumipy.query.expression.column.column_literal import python_to_expression
from typing import Union, Optional
from lumipy.query.expression.sql_value_type import SqlValType


class ScalarVariable(BaseVariable, BaseColumnExpression):
    """Class that represents a Luminesce scalar variable (@@variable). This behaves as a column expression
    and can be used anywhere you'd use a constant value in a query.

    Scalar variables are built from luminesce subqueries that resolve to a single value: i.e. a table with just one
    column and one row.
    """

    # Inherit from SourceColumn by analogy with the LiteralColumn class
    def __init__(self, var_name: str, value: Union[BaseTableExpression, str], data_type=None):
        """__init__ method of the ScalarVariable class.

        Args:
            var_name: name of the scalar variable. Must not conflict with any SQL keywords.
            value: the table expression that this scalar variable is to be built from or a str that contains a snippet
            of HC SQL for defining the scalar var (this is just for date(now) etc.)
            data_type: data type in the case that the input value is a SQL string.
        """

        if isinstance(value, BaseTableExpression):
            n_columns = len(value.get_columns())
            if n_columns != 1:
                raise ValueError(
                    f"Input table to scalar var definition does not resolve to a scalar value. "
                    f"Has {n_columns} columns, should have just one."
                )

            in_value = value
            data_type = value.get_columns()[0].get_type()
            sql_str = value.get_table_sql()

        elif isinstance(value, str):
            if data_type is None:
                raise ValueError("When defining a scalar value with a string you must explicitly define the data type.")
            in_value = python_to_expression(value)
            sql_str = value
        else:
            raise TypeError(
                f'Scalar variables can only be built from table expressions or str: received {type(value).__name__}'
            )

        BaseVariable.__init__(
            self,
            '@@',
            var_name,
            sql_str
        )

        # noinspection PyTypeChecker
        BaseColumnExpression.__init__(
            self,
            hash('scalar variable'),
            lambda x: f'@@{var_name}',
            lambda x: True,
            lambda x: data_type,
            'scalar variable',
            in_value
        )

    def get_col_dependencies(self):
        # Need to mask the column dependencies so they're not carried along when this is used in
        # a table unrelated to its parent. Will cause the column membership check to fail.
        return list()


class DateScalar(ScalarVariable):
    """Class representing scalar date variables

    """
    def __init__(self, date, delta):
        hash_str = str(abs(hash(date + str(delta))))[:5]
        name = f'd_{hash_str}'
        super().__init__(
            name,
            f"select date('{date}', '{delta} days')",
            SqlValType.Date
        )


class DateTimeScalar(ScalarVariable):
    """Class representing scalar datetime variables

    """

    def __init__(self, datetime, delta):
        hash_str = str(abs(hash(datetime + str(delta))))[:5]
        name = f'dt_{hash_str}'
        super().__init__(
            name,
            f"select datetime('{datetime}', '{delta} days')",
            SqlValType.DateTime
        )


def datetime_now(delta_days: Optional[int] = 0) -> DateTimeScalar:
    """Get a scalar variable representing the current date with an optional offset.

    Args:
        delta_days (Optional[int]): time delta in days. Defaults to 0.

    Returns:
        DateTimeScalar: Datetime scalar variable expression.
    """
    return DateTimeScalar('now', delta_days)


def date_now(delta_days: Optional[int] = 0) -> DateScalar:
    """Get a scalar variable representing the current datetime with an optional offset.

    Args:
        delta_days (Optional[int]): time delta in days. Defaults to 0.

    Returns:
        DateScalar: Date scalar variable expression.
    """
    return DateScalar('now', delta_days)