from typing import Union

from lumipy import window
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_ordering import BaseColumnOrdering
from lumipy.query.expression.column_op.aggregation_op import (
    MeanDrawdown, MaxDrawdown,
    MeanDrawdownLength, MaxDrawdownLength,
    GainLossRatio, SemiDeviation, MeanStdevRatio,
    PricesToReturns, ReturnsToPrices,
    Stdev
)
from lumipy.query.expression.window.function import WindowAggregate


class FinanceColumnFunctionAccessor:
    """FinanceColumnFunctionAccessor contains a collection of financial functions that act on a column expression such
    as maximum drawdown.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x):
        self.__x = x

    def max_drawdown(self) -> MaxDrawdown:
        """Apply a maximum drawdown calculation to this expression.

        Notes:
            Drawdown is calculated as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Max drawdown is then the maximum value of the drawdowns dd_i over the sequence of values.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Returns:
            MaxDrawdown: a MaxDrawdown instance representing the max drawdown over this column.
        """
        return MaxDrawdown(self.__x)

    def mean_drawdown(self) -> MeanDrawdown:
        """Apply a mean drawdown calculation to this expression.

        Notes:
            Drawdown is calculated as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Mean drawdown is then the mean value of the drawdown over the sequence of values.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Returns:
            MeanDrawdown: a MeanDrawdown instance representing the mean drawdown over this expression.
        """
        return MeanDrawdown(self.__x)

    def max_drawdown_length(self) -> MaxDrawdownLength:
        """Apply a max drawdown length calculation to this expression.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The max drawdown length is then the maximum value of the drawdown length in the time period.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Returns:
            MaxDrawdownLength: a MaxDrawdownLength instance representing the max drawdown length over this expression.
        """

        return MaxDrawdownLength(self.__x)

    def mean_drawdown_length(self) -> MeanDrawdownLength:
        """Apply a mean drawdown length calculation to this expression.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The mean drawdown length is then the mean value of the drawdown length in the time period.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the mean_drawdown method to the corresponding column in a .select()
            on the table variable.

        Returns:
            MeanDrawdownLength: a MeanDrawdownLength instance representing the mean drawdown length over this
            expression.
        """

        return MeanDrawdownLength(self.__x)

    def gain_loss_ratio(self) -> GainLossRatio:
        """Apply a gain-loss ratio calculation to this expression.

        Notes:
            Gain-loss ratio is the mean positive return of the series divided by the mean negative return of the series.

        Returns:
            GainLossRatio: a GainLossRatio instance representing the gain-loss ratio of this expression.
        """
        return GainLossRatio(self.__x)

    def semi_deviation(self) -> SemiDeviation:
        """Apply a semi-deviation calculation to this expression.

        Notes:
            Semi-deviation is the standard deviation of values in a returns series below the mean return value.

        Returns:
            SemiDeviation: a Semideviation instance representing the semi-deviation of this expression.
        """
        return SemiDeviation(self.__x)

    def information_ratio(self, y: BaseColumnExpression) -> MeanStdevRatio:
        """Apply an information ratio calculation to this expression.

        Notes:
            The information ratio is the mean excess return between a return series and a benchmark series divided by the
            standard deviation of the excess return.

        Args:
            y (BaseColumnExpression): the benchmark return series.

        Returns:
            MeanStdevRatio: a MeanStdevRatio instance representing the information ratio of this expression versus the
            given benchmark.
        """
        return MeanStdevRatio(self.__x - y)

    def tracking_error(self, y: BaseColumnExpression) -> Stdev:
        """Apply a tracking error calculation to this expression.

        Notes:
            The tracking error is the standard deviation of the difference between a return series and a benchmark.

        Args:
            y (BaseColumnExpression): the benchmark return series.

        Returns:
            Stdev: a Stdev instance representing the tracking error of this expression versus the given benchmark.
        """
        return Stdev(self.__x - y)

    def sharpe_ratio(self, r: Union[BaseColumnExpression, float]) -> MeanStdevRatio:
        """Apply a sharpe ratio calculation to this expression

        Notes:
            The Sharpe ratio is calculated as the mean excess return over the risk-free rate divided by the standard
            deviation of the excess return.

        Args:
            r (Union[BaseColumnExpression, float]): the risk-free rate of return. This can be a constant value (float
            input) or a series (column expression input).

        Returns:
            MeanStdevRatio: a MeanStdevRatio instance representing the Sharpe ratio of this expression.
        """
        return MeanStdevRatio(self.__x - r)

    def prices_to_returns(
            self,
            interval: int = 1,
            time_factor: float = 1.0,
            compound: bool = False,
            order: BaseColumnOrdering = None
    ) -> WindowAggregate:
        """Apply a computation for the returns series derived from an expression corresponding to a price series.

        Args:
            interval (int):
            time_factor (float): a time scale factor for annualisation.
            compound (bool): whether the time scale factor should be applied as a simple scale factor r*T or as a
            compounded calculation (r+1)**T
            order (BaseColumnOrdering): ordering to apply while computing the returns. This function works as a window
            function in SQL and is therefore applied before the ORDER BY clause. If the data are not already time
            -ordered you should supply an ordering with this argument.

        Returns:
            WindowAggregate: a WindowAggregate instance corresponding to the prices to returns calculation.
        """
        return WindowAggregate(window(orders=order), PricesToReturns(self.__x, interval, time_factor, compound))

    def returns_to_prices(
            self,
            initial: float,
            time_factor: float = 1.0,
            compound: bool = False,
            order: BaseColumnOrdering = None
    ) -> WindowAggregate:
        """Apply a computation for the price series derived from an expression corresponding to a returns series.

        Args:
            initial (float): the initial price to apply return factors to.
            time_factor (float): a time scale factor for anualisation.
            compound (bool): whether the time scale factor should be applied as a simple scale factor r*T or as a
            compounded calculation (r+1)**T
            order (BaseColumnOrdering): ordering to apply while computing the returns. This function works as a window
            function in SQL and is therefore applied before the ORDER BY clause. If the data are not already time
            -ordered you should supply an ordering with this argument.

        Returns:
            WindowAggregate: a WindowAggregate instance corresponding to the returns to prices calculation.
        """
        return WindowAggregate(window(orders=order), ReturnsToPrices(self.__x, initial, time_factor, compound))
