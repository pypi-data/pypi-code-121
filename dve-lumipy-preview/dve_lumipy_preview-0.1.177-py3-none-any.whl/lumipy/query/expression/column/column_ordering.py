from lumipy.query.expression.base_sql_expression import BaseSqlExpression
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import LiteralColumn
from lumipy.query.expression.column.column_alias import AliasedColumn
from lumipy.query.expression.sql_value_type import SqlValType
from abc import abstractmethod
from typing import Union


class BaseColumnOrdering(BaseSqlExpression):
    """Base class for column ordering expressions

    """

    @abstractmethod
    def __init__(self, column: Union[int, BaseColumnExpression], order_str: str):
        """__init__ method of the BaseColumnOrdering class.

        Args:
            column (Union[int, BaseColumnExpression]): column expression to order by.
            order_str (str): order direction string. Valid values are 'asc', 'desc' (case-insensitive).
        """

        if type(column) == AliasedColumn:
            # noinspection PyUnresolvedReferences
            # Pycharm can't detect that the above enforces that it's an AliasedColumn...
            # Unwrap the aliased column and order by the original SQL piece.
            ord_col = column.get_original()
        elif issubclass(type(column), BaseColumnExpression):
            ord_col = column
        elif isinstance(column, int):
            if column < 1:
                raise ValueError(f"Column indices start from 1. Received index int: {column}.")
            ord_col = LiteralColumn(column)
        else:
            raise TypeError(
                f"Received an invalid type as column for a column ordering: {type(column).__name__}."
            )

        self._order_col = ord_col

        super().__init__(
            f'{order_str} order',
            lambda x: f"{x.get_sql()} {order_str.upper()}",
            lambda x: True,  # Anything ever not orderable?
            lambda x: SqlValType.Ordering,
            ord_col
        )

    def get_ordering_column(self) -> BaseColumnExpression:
        """Get the column expression underlying this ordering expression.

        Returns:
            BaseColumnExpression: the underlying column expression.
        """
        return self._order_col


class AscendingOrder(BaseColumnOrdering):
    """Class representing an ascending column ordering.

    """
    def __init__(self, column: Union[int, BaseColumnExpression]):
        """__init__ method of the AscendingOrder class.

        Args:
            column (Union[int, BaseColumnExpression]): column expression or column index to order on. Index values
            start at 1.
        """
        super().__init__(column, "ASC")


class DescendingOrder(BaseColumnOrdering):
    """Class representing a descending column ordering.

    """

    def __init__(self, column: Union[int, BaseColumnExpression]):
        """__init__ method of the descending order class.

        Args:
            column (Union[int, BaseColumnExpression]): column expression or column index to order on. Index values
            start at 1.
        """
        super().__init__(column, "DESC")
