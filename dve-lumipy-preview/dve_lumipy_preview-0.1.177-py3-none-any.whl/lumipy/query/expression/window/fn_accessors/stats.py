from .base import BaseWindowFunctionAccessor
from ...column.column_base import BaseColumnExpression
from ..function import WindowAggregate
from typing import Union


class StatsWindowFunctionAccessor(BaseWindowFunctionAccessor):
    """StatsWindowFunctionAccessor contains a collection of statistical functions that act on one or more column
    expressions in a window such as skewness, kurtosis or covariance.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each window class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def covariance(self, x: BaseColumnExpression, y: BaseColumnExpression, ddof: int = 1) -> WindowAggregate:
        """Apply a covariance calculation in this window to the given expressions.
        This is an aggregation that will map two columns to a single value.

        Notes:
            Covariance is a statistical measure of the joint variability of two random variables. See
            https://en.wikipedia.org/wiki/Covariance

        Args:
            x (BaseColumnExpression): the first series in the covariance calculation.
            y (BaseColumnExpression): the second series in the covariance calculation.
            ddof (int): delta degrees of freedom (defaults to 1). Use ddof = 0 for the population covariance and
            ddof = 1 for the sample covariance.

        Returns:
           WindowAggregate : WindowAggregate a  instance representing the result of this calculation.
        """
        return self._apply(x.stats.covariance(y, ddof))

    def empirical_cdf(self, x: BaseColumnExpression, value: Union[int, float]) -> WindowAggregate:
        """Apply an empirical cumulative distribution function (CDF) calculation in this window to the given expression.
        This is an aggregation that will map a column to a single value.

        Notes:
            The empirical CDF is the cumulative distribution function of a sample. It is a step function that jumps by
            1/n at each of the n data points. This function returns the value of the empirical CDF at the given value.
            See
                https://en.wikipedia.org/wiki/Empirical_distribution_function

        Args:
            x (BaseColumnExpression): the expression to apply the windowed empirical CDF calculation to.
            value (Union[int, float]): the location to evaluate the empirical CDF at.

        Returns:
            WindowAggregate: an WindowAggregate instance representing the result of this calculation.
        """
        return self._apply(x.stats.empirical_cdf(value))

    def pearson_r(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a Pearson correlation coefficient calculation (Pearson's r) in this window to two given expressions.
        This is an aggregation that will map two columns to a single value.

        Notes:
            Pearson's r is a measure of the linear correlation between two random variables. See
            https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

        Args:
            x (BaseColumnExpression): the first series in the Pearson's r calculation.
            y (BaseColumnExpression): the second series in the Pearson's r calculation.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of this calculation.
        """
        return self._apply(x.stats.pearson_r(y))

    def spearman_r(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a Spearman rank correlation (Spearman's rho, or r_s) calculation in this window to the given
        expressions.
        This is an aggregation that will map two columns to a single value.

        Notes:
            Spearman's rho measures how monotonic (a function with a slope that does not change sign) the relationship
            between two random variables is. See
            https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient

        Args:
            x (BaseColumnExpression): the first series in the Spearman rank correlation calculation.
            y (BaseColumnExpression): the second series in the Spearman rank correlation calculation.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of this calculation.
        """
        return self._apply(x.stats.spearman_r(y))

    def median_abs_deviation(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a median absolute deviation calculation in this window to the given expression.
        This is an aggregation that will map a column to a single value.

        Notes:
            The median absolute deviation is a measure of the variability of a random variable. Unlike the standard
            deviation it is robust to the presence of outliers. See
            https://en.wikipedia.org/wiki/Median_absolute_deviation

        Args:
            x (BaseColumnExpression): the expression to apply the median absolute deviation to.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of the calculation.
        """
        return self._apply(x.stats.median_abs_deviation())

    def skewness(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a skewness calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            Skewness measures the degree of asymmetry of a random variable around its mean. See
            https://en.wikipedia.org/wiki/Skewness
            This calculation currently only supports sample skewness.

        Args:
            x (BaseColumnExpression): the expression to apply the skewness calculation to.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of the calculation.
        """
        return self._apply(x.stats.skewness())

    def kurtosis(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a kurtosis calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            Kurtosis measures how much probability density is in the tails (extremes) of a sample's distribution. See
            https://en.wikipedia.org/wiki/Kurtosis
            This function corresponds to the Pearson Kurtosis measure not the Fisher variant and currently only supports
            sample kurtosis.

        Args:
            x (BaseColumnExpression): the expression to apply the kurtosis calculation to.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of the calculation.
        """
        return self._apply(x.stats.kurtosis())

    def root_mean_square(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a root mean square (RMS) calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            RMS is the square root of the mean of the squared values of a set of values. It is a statistical measure of the
            spead of a random variable. See
            https://en.wikipedia.org/wiki/Root_mean_square

        Args:
            x (BaseColumnExpression): the expression to apply the RMS calculation to.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of the calculation.
        """

        return self._apply(x.stats.root_mean_square())

    def harmonic_mean(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a harmonic mean calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The harmonic mean is the reciprocal of the mean of the individual reciprocals of the values in a set. See
            https://en.wikipedia.org/wiki/Harmonic_mean

        Args:
            x (BaseColumnExpression): the expression to apply the harmonic mean calculation to.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of the calculation.
        """
        return self._apply(x.stats.harmonic_mean())

    def geometric_mean(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a geometric mean calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The geometric mean is the multiplicative equivalent of the normal arithmetic mean. It multiplies a set of n-many
            numbers together and then takes the n-th root of the result. See
            https://en.wikipedia.org/wiki/Geometric_mean

        Args:
            x (BaseColumnExpression): the expression to apply the geometric mean calculation to.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of the calculation.
        """
        return self._apply(x.stats.geometric_mean())

    def geometric_stdev(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a geometric standard deviation calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The geometric standard deviation measures the variability of a set of numbers where the appropriate mean to use
            is the geometric one (they are more appropriately combined by multiplication rather than addition). See
            https://en.wikipedia.org/wiki/Geometric_standard_deviation

        Args:
            x (BaseColumnExpression): the expression to apply the geometric standard deviation calculation to.

        Notes:
            This is computed as the exponential of the standard deviation of the natural log of each element in the set
                GSD = exp(stdev(log(x)))

        Returns:
            WindowAggregate: a WindowAggregate instance representing the rseult of this calculation.
        """
        return self._apply(x.log().stats.stdev()).exp()

    def entropy(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a Shannon entropy calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The Shannon entropy measures the average amount of "surprise" in a sequence of values. It can be considered a
            measure of variability.
            https://en.wikipedia.org/wiki/Entropy_(information_theory)
            It is calculated as
                S = -sum(p_i * log(p_i))
            where p_i is the probability of the ith value occurring computed from the sample (n occurrences / sample size).

        Args:
            x (BaseColumnExpression): the expression to apply the entropy calculation to.

        Notes:
            This function is equivalent to scipy.stats.entropy called with a single series and with the natural base.
            https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html

        Returns:
            WindowAggregate: an WindowAggregate instance that represents the result of this calculation.
        """

        return self._apply(x.stats.entropy())

    def interquartile_range(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply an interquartile range calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The interquartile range is the difference between the upper and lower quartiles. It can be used as a robust
            measure of the variability of a random variable. See
            https://en.wikipedia.org/wiki/Interquartile_range

        Args:
            x (BaseColumnExpression): the expression to apply the interquartile range calculation to.

        Returns:
            WindowAggregate: an WindowAggregate instance that represents the result of the calculation.
        """
        return self._apply(x.stats.interquartile_range())

    def interquantile_range(self, x: BaseColumnExpression, q1: float, q2: float) -> WindowAggregate:
        """Apply an interquantile range calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The interquantile range is the difference between two different quantiles. This is a generalisation of the
            interquartile range where q1=0.25 and q2=0.75.
            The upper quantile (q2) value must be greater than the lower quantile (q1) value.

        Args:
            x (BaseColumnExpression): the expression to apply the interquantile range calculation to.
            q1 (float): the lower quantile value.
            q2 (float): the upper quantile value.

        Returns:
            WindowAggregate: an WindowAggregate instance that represents the result of this calculation.
        """
        return self._apply(x.stats.interquantile_range(q1, q2))

    def coef_of_variation(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a coefficient of variation calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The coefficient of variation is the standard deviation scaled by the mean. It is a standardised measure of the
            dispersion of a random variable so distributions of different scale can be compared. See
            https://en.wikipedia.org/wiki/Coefficient_of_variation

        Args:
            x (BaseColumnExpression): the expression to apply the coefficient of variation calculation to.

        Returns:
            WindowAggregate: a WindowAggregate instance that represents the result of this calculation.
        """
        return self._apply(x.stats.coef_of_variation())

    def mean_stdev_ratio(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean-stdev ratio calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            This is a convenience function for computing the mean divided by the standard deviation. This is used in
            multiple financial statistics such as the Sharpe ratio and information ratio.

        Args:
            x (BaseColumnExpression): the expression to apply the mean stdev ratio calculation to.

        Returns:
            WindowAggregate: a WindowAggregate representing the result of this calculation.
        """
        return self._apply(x.stats.mean_stdev_ratio())

    def median(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a median calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The median is the value that separates the top and bottom half of a dataset. See
            https://en.wikipedia.org/wiki/Median
            It is equivalent to quantile 0.5, or the 50th percentile.

        Args:
            x (BaseColumnExpression): the expression to apply the median calculation to.

        Returns:
            WindowAggregate: a quantile instance representing the result of this calculation.
        """
        return self._apply(x.stats.median())

    def lower_quartile(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a lower quartile calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The lower quartile is the value that bounds the lower quarter of a dataset. See
            https://en.wikipedia.org/wiki/Quartile
            It is equivalent to quantile 0.25 or the 25th percentile.

        Args:
            x (BaseColumnExpression): the expression to apply the lower quartile calculation to.

        Returns:
            WindowAggregate: a quantile instance representing the result of this calculation.
        """
        return self._apply(x.stats.lower_quartile())

    def upper_quartile(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply an upper quartile calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The upper quartile is the value that bounds the upper quarter of a dataset. See
            https://en.wikipedia.org/wiki/Quartile
            It is equivalent to quantile 0.75 or the 75th percentile.

        Args:
            x (BaseColumnExpression): the expression to apply the upper quartile calculation to.

        Returns:
            WindowAggregate: a quantile instance representing the result of this calculation.
        """
        return self._apply(x.stats.upper_quartile())

    def quantile(self, x: BaseColumnExpression, q: float) -> WindowAggregate:
        """Apply a quantile function calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The quantile function of a given random variable and q value finds the value x where the probability of
            observing a value less than or equal to x is equal to q. See
            https://en.wikipedia.org/wiki/Quantile_function

        Args:
            x (BaseColumnExpression): the expression to apply the quantile calculation to.
            q (float): the quantile value. Must be between 0 and 1.

        Returns:
            WindowAggregate: a quantile instance representing the result of this calculation.
        """
        return self._apply(x.quantile(q))

    def stdev(self, x: BaseColumnExpression) -> WindowAggregate:
        """Apply a sample standard deviation calculation in this window to the given expression.
        This is an aggregation that will map to a single value.

        Notes:
            The standard deviation measures the dispersion of a set of values around the mean. See
            https://en.wikipedia.org/wiki/Standard_deviation

        Args:
            x (BaseColumnExpression): the expression to apply the standard deviation calculation to.

        Notes:
            This only calculates the sample standard deviation (delta degrees of freedom = 1)

        Returns:
            WindowAggregate: a WindowAggregate instance representing the result of this calculation.
        """
        return self._apply(x.stdev())
