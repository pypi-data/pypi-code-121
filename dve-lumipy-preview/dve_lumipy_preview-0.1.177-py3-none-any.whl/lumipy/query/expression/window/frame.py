from __future__ import annotations

from typing import Union

from lumipy.query.expression.column.column_literal import python_to_expression
from ..base_sql_expression import BaseSqlExpression
from ..sql_value_type import SqlValType


class WindowFrame(BaseSqlExpression):
    """Class representing the frame definition in the OVER clause of a SQL window function.

    """

    def __init__(self, lower: str, upper: str):
        """Constructor of the WindowFrame class.

        Args:
            lower (str): lower limit SQL string
            upper (str): upper limit SQL string
        """

        lower = python_to_expression(lower)
        upper = python_to_expression(upper)

        if lower.get_type() != SqlValType.Text or upper.get_type() != SqlValType.Text:
            t1 = lower.get_type().name
            t2 = upper.get_type().name
            raise TypeError(f'WindowFrame only takes specific string values. Received incompatible types: {t1} and {t2}')

        super().__init__(
            "window frame",
            lambda x, y: f'ROWS BETWEEN {x.get_py_value()} AND {y.get_py_value()}',
            lambda x, y: True,
            lambda x, y: SqlValType.ColumnSelection,
            python_to_expression(lower),
            python_to_expression(upper)
        )

    @staticmethod
    def _index_to_bound_str(index: Union[int, None], side: str) -> str:
        if index is not None and not isinstance(index, int):
            raise ValueError('Index must be an integer >= 0 or None')
        elif index is None:
            return f'UNBOUNDED {side}'
        elif index == 0:
            return 'CURRENT ROW'
        elif index > 0:
            return f'{index} {side}'
        else:
            raise ValueError('Index must be an integer >= 0 or None')

    @staticmethod
    def create(lower: Union[int, None], upper: Union[int, None]) -> WindowFrame:
        """Create WindowFrame instance from a pair or ints or Nones

        Args:
            lower (Union[int, None]): the int/None value that defines the lower window limit.
            upper (Union[int, None]): the int/None value that defined the upper window limit.

        Returns:
            WindowFrame: the corresponsing WindowFrame instance.
        """
        return WindowFrame(
            WindowFrame._index_to_bound_str(lower, 'PRECEDING'),
            WindowFrame._index_to_bound_str(upper, 'FOLLOWING')
        )
