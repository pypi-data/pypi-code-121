from typing import Union

from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column_op.aggregation_op import (
    Covariance, EmpiricalCdf,
    PearsonCorrelation, SpearmanRankCorrelation,
    MedianAbsoluteDeviation,
    Skewness, Kurtosis, RootMeanSquare,
    HarmonicMean, GeometricMean,
    Entropy, Quantile,
    InterquantileRange, InterquartileRange,
    CoefficientOfVariation, MeanStdevRatio,
    Stdev
)
from lumipy.query.expression.column_op.unary_op import Exp


class StatsColumnFunctionAccessor:
    """StatsColumnFunctionAccessor contains a collection of statistical functions that act on one or more column
    expressions such as skewness, kurtosis or covariance.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x):
        self.__x = x

    def covariance(self, y: BaseColumnExpression, ddof: int = 1) -> Covariance:
        """Apply a covariance calculation to this expression and the input.
        This is an aggregation that will map two columns to a single value.

        Notes:
            Covariance is a statistical measure of the joint variability of two random variables. See
                https://en.wikipedia.org/wiki/Covariance

        Args:
            y (BaseColumnExpression): the other series in the covariance calculation.
            ddof (int): delta degrees of freedom (defaults to 1). Use ddof = 0 for the population covariance and
            ddof = 1 for the sample covariance.

        Returns:
            Covariance: a Covariance instance representing the result of this calculation.
        """
        return Covariance(self.__x, y, ddof)

    def empirical_cdf(self, value: Union[int, float]) -> EmpiricalCdf:
        """Apply an empirical cumulative distribution function (CDF) calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The empirical CDF is the cumulative distribution function of a sample. It is a step function that jumps by
            1/n at each of the n data points. This function returns the value of the empirical CDF at the given value.
            See
                https://en.wikipedia.org/wiki/Empirical_distribution_function

        Args:
            value (Union[int, float]): the location to evaluate the empirical CDF at.

        Returns:
            EmpiricalCdf: an EmpiricalCdf instance representing the result of this calculation.
        """
        return EmpiricalCdf(self.__x, value)

    def pearson_r(self, y: BaseColumnExpression) -> PearsonCorrelation:
        """Apply a Pearson correlation coefficient calculation (Pearson's r) to this expression and the input.
        This is an aggregation that will map two columns to a single value.

        Notes:
            Pearson's r is a measure of the linear correlation between two random variables. See
                https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

        Args:
            y (BaseColumnExpression): the other series in the Pearson's r calculation.

        Returns:
            PearsonCorrelation: a PearsonCorrelation instance representing the result of this calculation.
        """
        return PearsonCorrelation(self.__x, y)

    def spearman_r(self, y: BaseColumnExpression) -> SpearmanRankCorrelation:
        """Apply a Spearman rank correlation (Spearman's rho, or r_s) calculation to this expression and the input.
        This is an aggregation that will map two columns to a single value.

        Notes:
            Spearman's rho measures how monotonic the relationship between two random variables is. See
                https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient

        Args:
            y (BaseColumnExpression): the other series in the Spearman rank correlation calculation.

        Returns:
            SpearmanRankCorrelation: a SpearmanRankCorrelation instance representing the result of this calculation.
        """
        return SpearmanRankCorrelation(self.__x, y)

    def median_abs_deviation(self) -> MedianAbsoluteDeviation:
        """Apply a median absolute deviation calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The median absolute deviation is a measure of the variability of a random variable. Unlike the standard
            deviation it is robust to the presence of outliers. See
                https://en.wikipedia.org/wiki/Median_absolute_deviation

        Returns:
            MedianAbsoluteDeviation: a MedianAbsoluteDeviation instance representing the result of the calculation.
        """
        return MedianAbsoluteDeviation(self.__x)

    def skewness(self) -> Skewness:
        """Apply a skewness calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            Skewness measures the degree of asymmetry of a random variable around its mean. See
                https://en.wikipedia.org/wiki/Skewness
            This calculation currently only supports sample skewness.

        Returns:
            Skewness: a Skewness instance representing the result of the calculation.
        """
        return Skewness(self.__x)

    def kurtosis(self) -> Kurtosis:
        """Apply a kurtosis calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            Kurtosis measures how much probability density is in the tails (extremes) of a sample's distribution. See
                https://en.wikipedia.org/wiki/Kurtosis
            This function corresponds to the Pearson Kurtosis measure not the Fisher one.
            This calculation currently only supports sample kurtosis.

        Returns:
            Kurtosis: a Kurtosis instance representing the result of the calculation.
        """
        return Kurtosis(self.__x)

    def root_mean_square(self) -> RootMeanSquare:
        """Apply a root mean square (RMS) calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            RMS is the square root of the mean of the squared values of a set of values. It is a statistical measure of the
            spead of a random variable. See
                https://en.wikipedia.org/wiki/Root_mean_square

        Returns:
            RootMeanSquare: a RootMeanSquare instance representing the result of the calculation.
        """
        return RootMeanSquare(self.__x)

    def harmonic_mean(self) -> HarmonicMean:
        """Apply a harmonic mean calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The harmonic mean is the reciprocal of the mean of the individual reciprocals of the values in a set. See
                https://en.wikipedia.org/wiki/Harmonic_mean

        Returns:
            HarmonicMean: a HarmonicMean instance representing the result of the calculation.
        """
        return HarmonicMean(self.__x)

    def geometric_mean(self) -> GeometricMean:
        """Apply a geometric mean calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The geometric mean is the multiplicative equivalent of the normal arithmetic mean. It multiplies a set of n-many
            numbers together and then takes the n-th root of the result. See
                https://en.wikipedia.org/wiki/Geometric_mean

        Returns:
            GeometricMean: a GeometricMean instance representing the result of the calculation.
        """
        return GeometricMean(self.__x)

    def geometric_stdev(self) -> Exp:
        """Apply a geometric standard deviation calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The geometric standard deviation measures the variability of a set of numbers where the appropriate mean to use
            is the geometric one (they are more appropriately combined by multiplication rather than addition). See
                https://en.wikipedia.org/wiki/Geometric_standard_deviation

            This is computed as the exponential of the standard deviation of the natural log of each element in the set
                GSD = exp(stdev(log(x)))

        Returns:
            Exp: an Exponential instance representing the rseult of this calculation.
        """
        return self.__x.log().stdev().exp()

    def entropy(self) -> Entropy:
        """Apply a Shannon entropy calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The Shannon entropy measures the average amount of "surprise" in a sequence of values. It can be considered a
            measure of variability.
                https://en.wikipedia.org/wiki/Entropy_(information_theory)
            It is calculated as
                S = -sum(p_i * log(p_i))
            where p_i is the probability of the ith value occurring computed from the sample (n occurrences / sample size).

            This function is equivalent to scipy.stats.entropy called with a single series and with the natural base.
                https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html

        Returns:
            Entropy: an Entropy instance that represents the result of this calculation.
        """
        return Entropy(self.__x)

    def interquartile_range(self) -> InterquartileRange:
        """Apply an interquartile range calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The interquartile range is the difference between the upper and lower quartiles. It can be used as a robust
            measure of the variability of a random variable. See
                https://en.wikipedia.org/wiki/Interquartile_range

        Returns:
            InterquartileRange: an InterquartileRange instance that represents the result of the calculation.
        """
        return InterquartileRange(self.__x)

    def interquantile_range(self, q1: float, q2: float) -> InterquantileRange:
        """Apply an interquantile range calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The interquantile range is the difference between two different quantiles. This is a generalisation of the
            interquartile range where q1=0.25 and q2=0.75.
            The upper quantile (q2) value must be greater than the lower quantile (q1) value.

        Args:
            q1 (float): the lower quantile value.
            q2 (float): the upper quantile value.

        Returns:
            InterquantileRange: an InterquantileRange instance that represents the result of this calculation.
        """
        return InterquantileRange(self.__x, q1, q2)

    def coef_of_variation(self) -> CoefficientOfVariation:
        """Apply a coefficient of variation calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The coefficient of variation is the standard deviation scaled by the mean. It is a standardised measure of the
            dispersion of a random variable so distributions of different scale can be compared. See
                https://en.wikipedia.org/wiki/Coefficient_of_variation

        Returns:
            CoefficientOfVariation: a CoefficientOfVariation instance that represents the result of this calculation.
        """
        return CoefficientOfVariation(self.__x)

    def mean_stdev_ratio(self) -> MeanStdevRatio:
        """Apply a mean-stdev ratio calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            This is a convenience function for computing the mean divided by the standard deviation. This is used in
            multiple financial statistics such as the Sharpe ratio and information ratio.

        Returns:
            MeanStdevRatio: a MeanStdevRatio representing the result of this calculation.
        """
        return MeanStdevRatio(self.__x)

    def median(self) -> Quantile:
        """Apply a median calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The median is the value that separates the top and bottom half of a dataset. See
                https://en.wikipedia.org/wiki/Median
            It is equivalent to quantile 0.5, or the 50th percentile.

        Returns:
            Quantile: a quantile instance representing the result of this calculation.
        """
        return Quantile(self.__x, 0.5)

    def lower_quartile(self) -> Quantile:
        """Apply a lower quartile calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The lower quartile is the value that bounds the lower quarter of a dataset. See
                https://en.wikipedia.org/wiki/Quartile
            It is equivalent to quantile 0.25 or the 25th percentile.

        Returns:
            Quantile: a quantile instance representing the result of this calculation.
        """
        return Quantile(self.__x, 0.25)

    def upper_quartile(self) -> Quantile:
        """Apply an upper quartile calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The upper quartile is the value that bounds the upper quarter of a dataset. See
                https://en.wikipedia.org/wiki/Quartile
            It is equivalent to quantile 0.75 or the 75th percentile.

        Returns:
            Quantile: a quantile instance representing the result of this calculation.
        """
        return Quantile(self.__x, 0.75)

    def quantile(self, q: float) -> Quantile:
        """Apply a quantile function calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The quantile function of a given random variable and q value finds the value x where the probability of
            observing a value less than or equal to x is equal to q. See
                https://en.wikipedia.org/wiki/Quantile_function

        Args:
            q (float): the quantile value. Must be between 0 and 1.

        Returns:
            Quantile: a quantile instance representing the result of this calculation.
        """
        return Quantile(self.__x, q)

    def stdev(self) -> Stdev:
        """Apply a sample standard deviation calculation to this expression.
        This is an aggregation that will map to a single value.

        Notes:
            The standard deviation measures the dispersion of a set of values around the mean. See
                https://en.wikipedia.org/wiki/Standard_deviation
            This only calculates the sample standard deviation (delta degrees of freedom = 1)

        Returns:
            Stdev: a Stdev isntance representing the result of this calculation.
        """
        return Stdev(self.__x)
