from typing import Optional

from lumipy.query.expression.column.column_ordering import BaseColumnOrdering
from lumipy.query.expression.column_op.aggregation_op import (
    CumeProd, Max, Min, Sum
)
from lumipy.query.expression.window.function import CumeDist
from lumipy.query.expression.window.function import WindowAggregate


class CumulativeColumnFunctionAccessor:
    """CumulativeColumnFunctionAccessor contains a collection of cumulative functions that act on a column such cumulative sum.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-str

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x):
        self.__x = x

    def __apply(self, op, order_by):
        from lumipy import window
        return WindowAggregate(window(orders=order_by), op(self.__x))

    def prod(self, order: Optional[BaseColumnOrdering] = None) -> WindowAggregate:
        """Apply a cumulative product to this expression.

        Args:
            order (Optional[BaseColumnOrdering]): optional ordering that will sort the data before applying the
            cumulative product

        Returns:
            WindowAggregate: object representing the column of data that will result from this calculation.

        """
        return self.__apply(CumeProd, order)

    def sum(self, order: Optional[BaseColumnOrdering] = None) -> WindowAggregate:
        """Apply a cumulative sum to this expression.

        Args:
            order Optional[BaseColumnOrdering]: optional ordering that will sort the data before applying the cumulative

        Returns:
            WindowAggregate: object representing the column of data that will result from this calculation.

        """
        return self.__apply(Sum, order)

    def min(self, order: Optional[BaseColumnOrdering] = None) -> WindowAggregate:
        """Apply a cumulative minimum to this expression.

        Args:
            order (Optional[BaseColumnOrdering]): optional ordering that will sort the data before applying the cumulative
            minimum.
        Returns:
            WindowAggregate: object representing the column of data that will result from this calculation.

        """
        return self.__apply(Min, order)

    def max(self, order: Optional[BaseColumnOrdering] = None) -> WindowAggregate:
        """Apply a cumulative maximum to this expression.

        Args:
            order (Optional[BaseColumnOrdering]): optional ordering that will sort the data before applying the cumulative
            maximum.

        Returns:
            WindowAggregate: object representing the column of data that will result from this calculation.
        """
        return self.__apply(Max, order)

    def dist(self) -> CumeDist:
        """Apply a cumulative distribution (quantile rank) to this expression.

        Notes:
            Equivalent to the following in SQL

                CUME_DIST() OVER(
                    ORDER BY <this column> ASC
                    )

            No interpolation is applied when computing the above expression. Each quantile result that comes from the
            cume_dist call is equivalent to percentile rank in pandas computed as follows

                df.column.rank(pct=True, method='first')

        Returns:
            CumeDist: column expression for computing the cumulative distribution of the column.
        """

        from lumipy import window
        return window(orders=self.__x.ascending(), lower=None).cume_dist()
