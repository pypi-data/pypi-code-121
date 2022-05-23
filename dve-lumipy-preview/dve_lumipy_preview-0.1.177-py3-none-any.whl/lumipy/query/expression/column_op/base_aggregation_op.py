from abc import abstractmethod

from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_alias import AliasedColumn
from lumipy.query.expression.column.column_literal import python_to_expression

from typing import Callable


class BaseAggregateColumn(BaseColumnExpression):
    """Base class for expressions that represent aggregate operations over a column/function of columns.
    For example: 'avg([column])'. All of these expressions will map a column/function of columns to a single value.

    """

    @abstractmethod
    def __init__(
            self,
            agg_op_name: str,
            sql_str_fn: Callable,
            type_check_fn: Callable,
            data_type_fn: Callable,
            *args: BaseColumnExpression
    ):
        """__init__ method of the BaseAggregateColumn class

        Args:
            column (BaseColumnExpression): the column expression to apply the aggregate expression to.
            agg_op_name: the name of the aggregate op.
            sql_str_fn (Callable):
            type_check_fn (Callable): SQL value type check function for the aggregate op.
            data_type_fn (Callable):
            *args (BaseColumnExpression):
        """

        args = [a.get_original() if isinstance(a, AliasedColumn) else a for a in args]
        args = [python_to_expression(a) for a in args]
        from .common import derive_table_hash
        source_table_hash = derive_table_hash(args)

        super().__init__(
            source_table_hash,
            sql_str_fn,
            type_check_fn,
            data_type_fn,
            agg_op_name,
            *args
        )
