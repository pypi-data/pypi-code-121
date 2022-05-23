from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn
from lumipy.query.expression.sql_value_type import numerics, SqlValType
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column.column_literal import python_to_expression


def between_0_1(val):
    return 0.0 <= val <= 1.0


class Count(BaseAggregateColumn):
    """Class representing a count column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for count class

        Args:
            column: column expression to apply count expression to.
        """
        super().__init__(
            'count',
            lambda x: f"count({x.get_sql()})",
            lambda x: True,
            lambda x: SqlValType.Int,
            column
        )


class Average(BaseAggregateColumn):
    """Class representing a mean column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for average class

        Args:
            column: column expression to apply average expression to.
        """
        super().__init__(
            'avg',
            lambda x: f"avg({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class Sum(BaseAggregateColumn):
    """Class representing a sum column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for sum class

        Args:
            column: column expression to apply sum expression to.
        """
        super().__init__(
            'total',
            lambda x: f"total({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: x,
            column,
        )


class Min(BaseAggregateColumn):
    """Class representing a min column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for min class

        Args:
            column: column expression to apply min expression to.
        """
        super().__init__(
            'min',
            lambda x: f"min({x.get_sql()})",
            lambda x: True,
            lambda x: x,
            column
        )


class Max(BaseAggregateColumn):
    """Class representing a max column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for max class

        Args:
            column: column expression to apply max expression to.
        """
        super().__init__(
            'max',
            lambda x: f"max({x.get_sql()})",
            lambda x: True,
            lambda x: x,
            column
        )


class Median(BaseAggregateColumn):
    """Class representing a median column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for median class

        Args:
            column: column expression to apply median expression to.
        """
        super().__init__(
            'median',
            lambda x: f"quantile({x.get_sql()}, 0.5)",
            lambda x: x in numerics,
            lambda x: x,
            column,
        )


class Stdev(BaseAggregateColumn):
    """Class representing a stdev column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for stdev class

        Args:
            column: column expression to apply stdev expression to.
        """
        super().__init__(
            'stdev',
            lambda x: f"window_stdev({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column,
        )


class Quantile(BaseAggregateColumn):
    """Class representing a quantile calculation over a column

    """

    def __init__(self, column: BaseColumnExpression, quantile: float):
        """__init__ method of the quantile class

        Args:
            column (BaseColumnExpression): column to apply quantile expression to
            quantile (float): the value of the quantile. Must be between 0 and 1.
        """

        quantile = python_to_expression(quantile)

        if not between_0_1(quantile.get_py_value()):
            raise ValueError(f"Quantile is only defined between 0 and 1. Was {quantile.get_py_value()}")

        super().__init__(
            'quantile',
            lambda x, y: f"quantile({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y == SqlValType.Double,
            lambda x, y: x,
            column,
            quantile
        )


class CumeProd(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "cume prod",
            lambda x: f"cumeprod({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: x,
            column
        )


class Covariance(BaseAggregateColumn):
    def __init__(self, column1, column2, ddof):
        super().__init__(
            'covariance',
            lambda x, y, z: f"covariance({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda x, y, z: x in numerics and y in numerics and z == SqlValType.Int,
            lambda x, y, z: SqlValType.Double,
            column1,
            column2,
            ddof
        )


class EmpiricalCdf(BaseAggregateColumn):
    def __init__(self, column, value):
        super().__init__(
            'empirical cdf',
            lambda x, y: f"empirical_cume_dist_function({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: x,
            column,
            value
        )


class Skewness(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "skewness",
            lambda x: f"skewness({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class Kurtosis(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "kurtosis",
            lambda x: f"kurtosis({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class RootMeanSquare(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "root mean square",
            lambda x: f"root_mean_square({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class HarmonicMean(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "harmonic mean",
            lambda x: f"harmonic_mean({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class GeometricMean(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "geometric mean",
            lambda x: f"geometric_mean({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class Entropy(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "entropy",
            lambda x: f"entropy({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class InterquartileRange(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "interquartile range",
            lambda x: f"interquartile_range({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class InterquantileRange(BaseAggregateColumn):
    def __init__(self, column, lower, upper):

        lower = python_to_expression(lower)
        upper = python_to_expression(upper)

        if not between_0_1(lower.get_py_value()):
            raise ValueError(f"Lower quantile is only defined between 0 and 1. Was {lower.get_py_value()}")
        if not between_0_1(upper.get_py_value()):
            raise ValueError(f"Upper quantile is only defined between 0 and 1. Was {upper.get_py_value()}")
        if upper.get_py_value() <= lower.get_py_value():
            raise ValueError(
                f"Upper quantile must be greater than lower quantile (Was upper = {upper.get_py_value()}, lower = {lower.get_py_value()})"
            )

        super().__init__(
            "interquantile range",
            lambda x, y, z: f"interquantile_range({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda x, y, z: x in numerics and y == SqlValType.Double and z == SqlValType.Double,
            lambda x, y, z: SqlValType.Double,
            column,
            lower,
            upper
        )


class PearsonCorrelation(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "pearson correlation",
            lambda x, y: f"pearson_correlation({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class SpearmanRankCorrelation(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "spearman rank correlation",
            lambda x, y: f"spearman_rank_correlation({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class MeanSquaredError(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "mean squared error",
            lambda x, y: f"mean_squared_error({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class MeanAbsoluteError(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "mean absolute error",
            lambda x, y: f"mean_absolute_error({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class MeanFractionalAbsoluteError(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "mean fractional absolute error",
            lambda x, y: f"mean_fractional_absolute_error({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class MedianAbsoluteDeviation(BaseAggregateColumn):
    def __init__(self, column1):
        super().__init__(
            "median absolute deviation",
            lambda x: f"median_absolute_deviation({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column1
        )


class GainLossRatio(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "gain loss ratio",
            lambda x: f"gain_loss_ratio({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Double,
            column
        )


class SemiDeviation(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "semi deviation",
            lambda x: f"semi_deviation({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class Drawdown(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "drawdown",
            lambda x: f"drawdown({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Double,
            column
        )


class MaxDrawdown(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "max drawdown",
            lambda x: f"max_drawdown({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Double,
            column
        )


class MeanDrawdown(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "mean duration",
            lambda x: f"mean_drawdown({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Double,
            column
        )


class DrawdownLength(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "drawdown length",
            lambda x: f"drawdown_length({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Int,
            column
        )


class MaxDrawdownLength(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "max drawdown length",
            lambda x: f"max_drawdown_length({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Int,
            column
        )


class MeanDrawdownLength(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "mean drawdown length",
            lambda x: f"mean_drawdown_length({x.get_sql()})",
            lambda x: x == SqlValType.Double,
            lambda x: SqlValType.Double,
            column
        )


class LinearRegressionAlpha(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "linear regression alpha",
            lambda x, y: f"linear_regression_alpha({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class LinearRegressionBeta(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "linear regression beta",
            lambda x, y: f"linear_regression_beta({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class LinearRegressionAlphaError(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "linear regression alpha error",
            lambda x, y: f"linear_regression_alpha_error({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class LinearRegressionBetaError(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "linear regression beta error",
            lambda x, y: f"linear_regression_beta_error({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class PricesToReturns(BaseAggregateColumn):
    def __init__(self, prices, interval, time_factor, compounded):

        interval = python_to_expression(interval)
        time_factor = python_to_expression(time_factor)

        if interval.get_py_value() < 1 or interval.get_type() != SqlValType.Int:
            raise ValueError(f"Prices to returns interval must be an integer greater than zero - was {interval.get_py_value()}.")
        if time_factor.get_py_value() <= 0.0:
            raise ValueError(f"Prices to returns time factor must be greater than zero - was {time_factor.get_py_value()}.")

        # p, i, t, c -> prices, interval, time factor, compounded
        super().__init__(
            "prices to returns",
            lambda p, i, t, c: f"prices_to_returns({p.get_sql()}, {i.get_sql()}, {t.get_sql()}, {c.get_sql()})",
            lambda p, i, t, c: p == SqlValType.Double and i == SqlValType.Int and t in numerics and c == SqlValType.Boolean,
            lambda p, i, t, c: SqlValType.Double,
            prices,
            interval,
            time_factor,
            compounded
        )


class ReturnsToPrices(BaseAggregateColumn):
    def __init__(self, returns, start_price, time_factor, compound):

        start_price = python_to_expression(start_price)
        time_factor = python_to_expression(time_factor)

        if start_price.get_py_value() <= 0.0:
            raise ValueError(f"Returns to prices start price must be greater than zero - was {start_price.get_py_value()}.")
        if time_factor.get_py_value() <= 0.0:
            raise ValueError(f"Prices to returns time factor must be greater than zero - was {time_factor.get_py_value()}.")

        # r, s, t, c -> returns, start price, time factor, compounded
        super().__init__(
            "returns to prices",
            lambda r, s, t, c: f"returns_to_prices({r.get_sql()}, {s.get_sql()}, {t.get_sql()}, {c.get_sql()})",
            lambda r, s, t, c: r == SqlValType.Double and s in numerics and t in numerics and c == SqlValType.Boolean,
            lambda p, i, t, c: SqlValType.Double,
            returns,
            start_price,
            time_factor,
            compound
        )


class MeanStdevRatio(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "mean stdev ratio",
            lambda x: f"mean_stdev_ratio({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class CoefficientOfVariation(BaseAggregateColumn):
    def __init__(self, column):
        super().__init__(
            "coefficient of variation",
            lambda x: f"coefficient_of_variation({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double,
            column
        )


class MinkowskiDistance(BaseAggregateColumn):
    def __init__(self, column1, column2, power):
        super().__init__(
            "minkowski distance",
            lambda x, y, z: f"minkowski_distance({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda x, y, z: x in numerics and y in numerics and z in numerics,
            lambda x, y, z: SqlValType.Double,
            column1,
            column2,
            power
        )


class ChebyshevDistance(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "chebyshev distance",
            lambda x, y: f"chebyshev_distance({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class ManhattanDistance(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "manhattan distance",
            lambda x, y: f"manhattan_distance({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class EuclideanDistance(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "euclidean distance",
            lambda x, y: f"euclidean_distance({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class CanberraDistance(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "canberra distance",
            lambda x, y: f"canberra_distance({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class BrayCurtisDistance(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "braycurtis distance",
            lambda x, y: f"braycurtis_distance({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class CosineDistance(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "cosine distance",
            lambda x, y: f"cosine_distance({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y in numerics,
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class PrecisionScore(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "precision score",
            lambda x, y: f"precision_score({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in [SqlValType.Int, SqlValType.Boolean] and y in [SqlValType.Int, SqlValType.Boolean],
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class RecallScore(BaseAggregateColumn):
    def __init__(self, column1, column2):
        super().__init__(
            "recall score",
            lambda x, y: f"recall_score({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in [SqlValType.Int, SqlValType.Boolean] and y in [SqlValType.Int, SqlValType.Boolean],
            lambda x, y: SqlValType.Double,
            column1,
            column2
        )


class FBetaScore(BaseAggregateColumn):
    def __init__(self, column1, column2, beta):
        super().__init__(
            "f beta score",
            lambda x, y, z: f"fbeta_score({x.get_sql()}, {y.get_sql()}, {z.get_sql()})",
            lambda x, y, z: x in [SqlValType.Int, SqlValType.Boolean] and y in [SqlValType.Int, SqlValType.Boolean] and z in [SqlValType.Int, SqlValType.Double],
            lambda x, y, z: SqlValType.Double,
            column1,
            column2,
            beta
        )
