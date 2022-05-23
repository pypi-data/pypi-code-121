from abc import abstractmethod

from ..column.column_base import BaseColumnExpression
from ..column.column_literal import python_to_expression
from lumipy.query.expression.column.column_alias import AliasedColumn
from typing import Callable


class BaseScalarOp(BaseColumnExpression):
    """Base class for expressions that represent scalar operations on columns: i.e. functions that map a column of
    values to another column of values.

    """

    @abstractmethod
    def __init__(
            self,
            op_name: str,
            sql_op_fn: Callable,
            type_check_fn: Callable,
            return_type_fn: Callable,
            *values: BaseColumnExpression
    ):
        """__init__ method of the BaseScalarOp class.

        Args:
            op_name (str): name of the scalar column op.
            sql_op_fn (Callable): function that takes SQL string pieces and makes the SQL piece for this op
            type_check_fn (Callable): function that checks the sql value types of the parents.
            return_type_fn (Callable): function that determines the output sql value type of this expression.
            *values (BaseColumnExpression): input values to the scalar column op expression. Must be a column expression
            (inheritor of BaseColumnExpression)
        """

        values = [v.get_original() if isinstance(v, AliasedColumn) else v for v in values]
        values = [python_to_expression(v) for v in values]
        from .common import derive_table_hash
        table_hash = derive_table_hash(values)

        super().__init__(
            table_hash,
            sql_op_fn,
            type_check_fn,
            return_type_fn,
            op_name,
            *values
        )
