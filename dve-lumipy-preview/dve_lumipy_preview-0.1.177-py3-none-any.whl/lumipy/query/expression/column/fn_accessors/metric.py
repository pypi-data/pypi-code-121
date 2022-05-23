from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column_op.aggregation_op import (
    MeanSquaredError, MeanAbsoluteError, MeanFractionalAbsoluteError,
    MinkowskiDistance, ChebyshevDistance, ManhattanDistance,
    EuclideanDistance, CanberraDistance, BrayCurtisDistance,
    CosineDistance, PrecisionScore, RecallScore, FBetaScore
)
from typing import Union, Optional


class MetricColumnFunctionAccessor:
    """MetricColumnFunctionAccessor contains a collection of metrics and statistical similarity measures between the
    expression and another column expression. These are all aggregate functions that map two columns of data to a single
    value.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x):
        self.__x = x

    def mean_squared_error(self, y: BaseColumnExpression) -> MeanSquaredError:
        """Apply a mean squared error calculation to this expression and another.

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            MeanSquaredError: a MeanSquaredError instance representing the mean square error metric calculation.
        """
        return MeanSquaredError(self.__x, y)

    def mean_absolute_error(self, y: BaseColumnExpression) -> MeanAbsoluteError:
        """Apply a mean absolute error calculation to this expression and another.

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            MeanAbsoluteError: a MeanAbsoluteError instance representing the mean absolute error metric calculation.
        """
        return MeanAbsoluteError(self.__x, y)

    def mean_fractional_absolute_error(self, y: BaseColumnExpression) -> MeanFractionalAbsoluteError:
        """Apply a mean fractional absolute error calculation to this expression and another.

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            MeanFractionalAbsoluteError: a MeanAbsoluteFractionalError instance representing the mean fractional
            absolute error calculation.
        """
        return MeanFractionalAbsoluteError(self.__x, y)

    def minkowski_distance(self, y: BaseColumnExpression, p: Union[float, int]) -> MinkowskiDistance:
        """Apply a Minkowski distance calculation to this expression and another

        Notes:
            The Minkowski distance is a generalisation of the Euclidean (p=2) or Manhattan (p=1) distance to other powers p.
            See
                https://en.wikipedia.org/wiki/Minkowski_distance

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.
            p (int): the order to use in the Minkowski distance calculation.

        Returns:
            MinkowskiDistance: a MinkowskiDistance instance representing the calculation.

        """
        return MinkowskiDistance(self.__x, y, p)

    def chebyshev_distance(self, y: BaseColumnExpression) -> ChebyshevDistance:
        """Apply a Chebyshev distance calculation to this expression and another.

        Notes:
            The Chebyshev distance is the greatest difference between dimension values of two vectors. It is equivalent to
            the Minkowski distance as p → ∞
            See
                https://en.wikipedia.org/wiki/Chebyshev_distance

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            ChebyshevDistance: a ChebyshevDistance instance representing the calculation.

        """
        return ChebyshevDistance(self.__x, y)

    def manhattan_distance(self, y: BaseColumnExpression) -> ManhattanDistance:
        """Apply a Manhattan distance calculation to this expression and another.

        Notes:
            The Manhattan distance (aka the taxicab distance) is the absolute sum of differences between the elements of two
            vectors. It is analogous the distance traced out by a taxicab moving along a city grid like Manhattan where the
            diagonal distance is the sum of the sides of the squares.
            See
                https://en.wikipedia.org/wiki/Taxicab_geometry

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            ManhattanDistance: a ManhattanDistance instance representing the calculation.

        """
        return ManhattanDistance(self.__x, y)

    def euclidean_distance(self, y: BaseColumnExpression) -> EuclideanDistance:
        """Apply a Euclidean distance calculation to this expression and another.

        Notes:
            The Euclidean distance is the familiar 'as the crow flies' distance. It is the square root of the sum of squared
            differences between the elements of two vectors.
            See
                https://en.wikipedia.org/wiki/Euclidean_distance

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            EuclideanDistance: a EuclideanDistance instance representing the calculation.

        """
        return EuclideanDistance(self.__x, y)

    def canberra_distance(self, y: BaseColumnExpression) -> CanberraDistance:
        """Apply a Canberra distance calculation to this expression and another.

        Notes:
            The Canberra distance is the elementwise sum of absolute differences between elements divided by the sum of
            their absolute values. It can be considered a weighted version of the Manhattan distance.
            See
                https://en.wikipedia.org/wiki/Canberra_distance

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            CanberraDistance: a CanberraDistance instance representing the calculation.

        """
        return CanberraDistance(self.__x, y)

    def braycurtis_distance(self, y: BaseColumnExpression) -> BrayCurtisDistance:
        """Apply a Bray-Curtis distance calculation to this expression and another.

        Notes:
            The Bray-Curtis distance is the elementwise sum of absolute differences between elements divided by the absolute
            value of their sum. It behaves like a fractional version of the Manhattan distance.

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            BrayCurtisDistance: a BrayCurtisDistance instance representing the calculation.

        """
        return BrayCurtisDistance(self.__x, y)

    def cosine_distance(self, y: BaseColumnExpression) -> CosineDistance:
        """Apply a cosine distance calculation to this expression and another.

        Notes:
            The cosine distance is the cosine of the angle between two vectors subtracted from 1.
            See
                https://en.wikipedia.org/wiki/Cosine_similarity

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            CosineDistance: a CosineDistance instance representing the calculation.

        """
        return CosineDistance(self.__x, y)

    def precision_score(self, y: BaseColumnExpression) -> PrecisionScore:
        """Apply a precision score calculation to this expression and another.

        Notes:
            Precision is a classification performance metric which measures the fraction of true positive events in a
            set of events that a classifier has predicted to be positive. It is calculated as follows

                precision = tp / (tp + fp)

            where tp is the number of true positives and fp is the number of false positives. Precision is a measure of the
            purity of the classifier's positive predictions.
            See
                https://en.wikipedia.org/wiki/Precision_and_recall

            Precision is also known as the positive predictive value and purity.

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            PrecisionScore: a PrecisionScore instance representing the calculation.

        """
        return PrecisionScore(self.__x, y)

    def recall_score(self, y: BaseColumnExpression) -> RecallScore:
        """Apply a recall score calculation to this expression and another.

        Notes:
            Recall is a classification performance metric which measures the fraction of positive events that are
            successfully predicted by a classifier. It is calculated as follows

                recall = tp / (tp + fn)

            where tp is the number of true positives and fn is the number of false negatives. Recall is a measure of the
            efficiency of the classifier at retrieving positive events.
            See
                https://en.wikipedia.org/wiki/Precision_and_recall

            Recall is also known as sensitivity, hit rate, true positive rate (TPR) and efficiency.

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.

        Returns:
            RecallScore: a RecallScore instance representing the calculation.

        """
        return RecallScore(self.__x, y)

    def f_score(self, y: BaseColumnExpression, beta: Optional[float]) -> FBetaScore:
        """Apply an F-score calculation to this expression and another

        Notes:
            The F-score is classifier performance metric which measures accuracy. It is defined as the weighted harmonic
            mean of precision and recall scores. The beta parameter controls the relative weighting of these two metrics.

            The most common value of beta is 1: this is the F_1 score (aka balanced F-score). It weights precision and
            recall evenly. Values of beta greater than 1 weight recall higher than precision and less than 1 weights
            precision higher than recall.

            See
                https://en.wikipedia.org/wiki/F-score

        Args:
            y (BaseColumnExpression): an expression corresponding to the other series.
            beta (Optional[float]): the value of beta to use in the calculation (Defaults to 1.0).

        Returns:
            FBetaScore: a FBetaScore instance representing the calculation.

        """
        return FBetaScore(self.__x, y, beta)
