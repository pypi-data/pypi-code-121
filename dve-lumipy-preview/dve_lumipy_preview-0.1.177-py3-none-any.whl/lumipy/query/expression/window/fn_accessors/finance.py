from typing import Union

from lumipy.query.expression.column_op.aggregation_op import (
    Drawdown, DrawdownLength
)
from .base import BaseWindowFunctionAccessor
from ..function import WindowAggregate
from ...column.column_base import BaseColumnExpression
from ...column_op.binary_op import Mul


class FinanceWindowFunctionAccessor(BaseWindowFunctionAccessor):
    """FinanceColumnFunctionAccessor contains a collection of financial functions that act in a window on one or more
    column expressions such as maximum drawdown or information ratio.

    This and the other accessor classes behave like a namespace and keep the different window methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def drawdown(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a drawdown calculation in this window to the given expression.

        Notes:
            Drawdown is calculated as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i in this window.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input prices series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the max drawdown over this column.
        """
        return self._apply(Drawdown(x))

    def mean_drawdown(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean drawdown calculation in this window to the given expression.

        Notes:
            Drawdown is calculated as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Mean drawdown is then the mean value of the drawdown over the sequence of values.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input prices series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the mean drawdown over this expression.
        """
        return self._apply(x.finance.mean_drawdown())

    def max_drawdown(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a max drawdown calculation in this window to the given expression.

        Notes:
            Drawdown is calculated as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Mean drawdown is then the max value of the drawdown over the sequence of values.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input prices series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the max drawdown over this expression.
        """
        return self._apply(x.finance.max_drawdown())

    def drawdown_length(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a drawdown length calculation in this window to the given expression.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the mean_drawdown method to the corresponding column in a .select()
            on the table variable.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input prices series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the drawdown length over this expression.
        """
        return self._apply(DrawdownLength(x))

    def mean_drawdown_length(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean drawdown length calculation in this window to the given expression.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The mean drawdown length is then the mean value of the drawdown length in the time period.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the mean_drawdown method to the corresponding column in a .select()
            on the table variable.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input prices series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the mean drawdown length over this expression.
        """
        return self._apply(x.finance.mean_drawdown_length())

    def max_drawdown_length(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a max drawdown length calculation in this window to q given expression.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The max drawdown length is then the maximum value of the drawdown length in the time period.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input prices series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the max drawdown length over this expression.
        """
        return self._apply(x.finance.max_drawdown_length())

    def gain_loss_ratio(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a gain-loss ratio calculation in this window to a given expression.

        Notes:
            Gain-loss ratio is the mean positive return of the series divided by the mean negative return of the series.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the gain-loss ratio of this expression.
        """
        return self._apply(x.finance.gain_loss_ratio())

    def semi_deviation(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a semi-deviation calculation in this window to a given expression.

        Notes:
            Semi-deviation is the standard deviation of values in a returns series below the mean return value.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the semi-deviation of this expression.
        """
        return self._apply(x.finance.semi_deviation())

    def gain_mean(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a gain mean calculation in this window to a given expression.

        Notes:
            The gain mean is the arithmetic mean of positive returns.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the gain mean of this expression.
        """
        return self._window.filter(x >= 0).mean(x)

    def loss_mean(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a loss mean calculation in this window to a given expression.

        Notes:
            The loss mean is the arithmetic mean of negative returns.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the loss mean of this expression.
        """
        return self._window.filter(x < 0).mean(x)

    def gain_stdev(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a gain standard deviation calculation in this window to a given expression.

        Notes:
            The gain standard deviation is the standard deviation of positive returns.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the gain standard deviation of this expression.
        """
        return self._window.filter(x >= 0).stats.stdev(x)

    def loss_stdev(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a loss standard deviation calculation in this window to a given expression.

        Notes:
            The loss standard deviation is the standard deviation of positive returns.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the loss standard deviation of this expression.
        """
        return self._window.filter(x < 0).stats.stdev(x)

    def downside_deviation(self, x: BaseColumnExpression, threshold: float) -> WindowAggregate:
        """Apply a loss downside deviation calculation in this window to a given expression.

        Notes:
            The downside deviation is the standard deviation of returns below a given threshold.

        Args:
            x (BaseColumnExpression): an expression corresponding to the input returns series.
            threshold (float): the threshold value of the downside deviation.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the loss standard deviation of this expression.
        """
        return self._window.filter(x < threshold).stats.stdev(x)

    def information_ratio(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply an information ratio calculation in this window for the given expressions.

        Notes:
            The information ratio is the mean excess return between a return series and a benchmark series divided by the
            standard deviation of the excess return.

        Args:
            x (BaseColumnExpression): an expression corresponding to the first returns series.
            y (BaseColumnExpression): an expression corresponding to the second returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the information ratio of this expression versus the
            given benchmark.
        """
        return self._window.stats.mean_stdev_ratio(x - y)

    def tracking_error(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a tracking error calculation in this window for the given expressions.

        Notes:
            The tracking error is the standard deviation of the difference between a return series and a benchmark.

        Args:
            x (BaseColumnExpression): an expression corresponding to the first returns series.
            y (BaseColumnExpression): an expression corresponding to the second returns series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the tracking error of this expression versus the
            given benchmark.
        """
        return self._window.stats.stdev(x - y)

    def sharpe_ratio(self, x: BaseColumnExpression, r: Union[float, BaseColumnExpression]) -> WindowAggregate:
        """Apply a sharpe ratio calculation in this window for the given expressions.

        Notes:
            The Sharpe ratio is calculated as the mean excess return over the risk free rate divided by the standard
            deviation of the excess return.

        Args:
            x (BaseColumnExpression): an expression corresponding to the returns series.
            r (Union[BaseColumnExpression, float]): the risk-free rate of return. This can be a constant value (float
            input) or a series (column expression input).

        Returns:
            WindowAggregate: a WindowAggregate instance representing the Sharpe ratio of this expression.
        """
        return self._window.stats.mean_stdev_ratio(x - r)

    def volatility(
            self,
            x: BaseColumnExpression,
            time_factor: float
    ) -> WindowAggregate:
        """Apply a volatility calculation in this window to a given expression.

        Notes:
            Volatility is calculated as the standard deviation of log returns in a given window.
            https://en.wikipedia.org/wiki/Volatility_(finance)#Mathematical_definition

        Args:
            x (BaseColumnExpression): an expression corresponding to the input log returns series.
            time_factor (float): an annualisation factor to apply to the volatility value.

        Notes:
            The time factor is applied as
                vol = stdev(x) * sqrt(T)
            where T is the time factor and x is log returns.

        Returns:
            Mul: a Mul instance representing the volatility of the input expression in this window.
        """
        return self._window.stats.stdev(x) * (time_factor**0.5)
