from typing import Union

from ..column_base import BaseColumnExpression
from ...column_op.binary_op import Strftime


class DatetimeColumnFunctionAccessor:
    """DatetimeColumnFunctionAccessor contains a collection of datetime functions that act on a column such strftime.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x):
        self.__x = x

    def strftime(self, dt_format: Union[str, BaseColumnExpression]) -> Strftime:
        """Apply a strftime expression to this column expression.

        Strftime will take a date or datetime value to a string/int value given a format string.

        Args:
            dt_format (Union[str, BaseColumnExpression]): datetime format string to supply to strftime. Can be a python
            string literal or a string-valued column expression.

        Returns:
            Strftime: Strftime instance representing the expression applied to this column.
        """
        return Strftime(dt_format, self.__x)

    def unixepoch(self) -> Strftime:
        """Apply a strftime expression returns the unix epoch of a datetime-valued column expression.

        Returns:
            Strftime: Strftime instance representing the expression applied to this column.
        """
        return self.__x.dt.strftime('%s')
