from typing import Optional

from .base import BaseWindowFunctionAccessor
from ..function import WindowAggregate
from ...column.column_base import BaseColumnExpression


class MetricWindowFunctionAccessor(BaseWindowFunctionAccessor):
    """MetricWindowFunctionAccessor contains a collection of metrics and statistical similarity measures between the
    expression and another column expression applied in a window. These are all aggregate functions that map two columns
    of data to a single value.

    This and the other accessor classes behave like a namespace and keep the different window methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def mean_squared_error(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean squared error calculation in this window to the given expressions.

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the mean square error metric calculation.
        """
        return self._apply(x.metric.mean_squared_error(y))

    def mean_absolute_error(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean absolute error calculation in this window to the given expressions.

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the mean absolute error metric calculation.
        """
        return self._apply(x.metric.mean_absolute_error(y))

    def mean_fractional_absolute_error(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a mean fractional absolute error calculation in this window to the given expressions.

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the mean fractional absolute error
            calculation.
        """
        return self._apply(x.metric.mean_fractional_absolute_error(y))

    def minkowski_distance(self, x: BaseColumnExpression, y: BaseColumnExpression, p: int) -> WindowAggregate:
        """Apply a Minkowski distance calculation in this window between the two given expressions.

        Notes:
            The Minkowski distance is a generalisation of the Euclidean (p=2) or Manhattan (p=1) distance to other powers p.
            See
                https://en.wikipedia.org/wiki/Minkowski_distance

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.
            p (int): the order to use in the Minkowski distance calculation.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the minkowski distance calculation.
        """
        return self._apply(x.metric.minkowski_distance(y, p))

    def chebyshev_distance(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a Chebyshev distance calculation in this window between the two given expressions.

        Notes:
            The Chebyshev distance is the greatest difference between dimension values of two vectors. It is equivalent to
            the Minkowski distance as p → ∞
            See
                https://en.wikipedia.org/wiki/Chebyshev_distance

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the Chebyshev distance calculation.

        """
        return self._apply(x.metric.chebyshev_distance(y))

    def manhattan_distance(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a Manhattan distance calculation in this window between the two given expressions.

        Notes:
            The Manhattan distance (aka the taxicab distance) is the absolute sum of differences between the elements of two
            vectors. It is analogous the distance traced out by a taxicab moving along a city grid like Manhattan where the
            diagonal distance is the sum of the sides of the squares.
            See
                https://en.wikipedia.org/wiki/Taxicab_geometry

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the Manhattan distance calculation.

        """
        return self._apply(x.metric.manhattan_distance(y))

    def euclidean_distance(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a Euclidean distance calculation in this window between the two given expressions.

        Notes:
            The Euclidean distance is the familiar 'as the crow flies' distance. It is the square root of the sum of squared
            differences between the elements of two vectors.
            See
                https://en.wikipedia.org/wiki/Euclidean_distance

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the Euclidean distance calculation.

        """
        return self._apply(x.metric.euclidean_distance(y))

    def canberra_distance(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a Canberra distance calculation in this window between the two given expressions.

        Notes:
            The Canberra distance is the elementwise sum of absolute differences between elements divided by the sum of
            their absolute values. It can be considered a weighted version of the Manhattan distance.
            See
                https://en.wikipedia.org/wiki/Canberra_distance

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the Canberra distance calculation.

        """
        return self._apply(x.metric.canberra_distance(y))

    def braycurtis_distance(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a bray-curtis distance calculation in this window between the two given expressions.

        Notes:
            The Bray-Curtis distance is the elementwise sum of absolute differences between elements divided by the absolute
            value of their sum. It behaves like a fractional version of the Manhattan distance.

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the Bray-Curtis distance calculation.

        """
        return self._apply(x.metric.braycurtis_distance(y))

    def cosine_distance(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a cosine distance calculation in this window between the two given expressions.

        Notes:
            The cosine distance is the cosine of the angle between two vectors subtracted from 1.
            See
                https://en.wikipedia.org/wiki/Cosine_similarity

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the cosine distance calculation.

        """
        return self._apply(x.metric.cosine_distance(y))

    def precision_score(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a precision score calculation in this window between the two given expressions.

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
            x (BaseColumnExpression): an expression corresponding to the first series. Must be boolean or an integer
            equal to zero or one.
            y (BaseColumnExpression): an expression corresponding to the second series. Must be boolean or an integer
            equal to zero or one.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the precision score calculation.

        """
        return self._apply(x.metric.precision_score(y))

    def recall_score(self, x: BaseColumnExpression, y: BaseColumnExpression) -> WindowAggregate:
        """Apply a recall score calculation in this window between the two given expressions.

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
            x (BaseColumnExpression): an expression corresponding to the first series. Must be boolean or an integer
            equal to zero or one.
            y (BaseColumnExpression): an expression corresponding to the second series. Must be boolean or an integer
            equal to zero or one.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the recall score calculation.

        """
        return self._apply(x.metric.recall_score(y))

    def f_score(self, x: BaseColumnExpression, y: BaseColumnExpression, beta: Optional[float] = 1.0) -> WindowAggregate:
        """Apply an F-score calculation in this window between the two given expressions.

        Notes:
            The F-score is classifier performance metric which measures accuracy. It is defined as the weighted harmonic
            mean of precision and recall scores. The beta parameter controls the relative weighting of these two metrics.

            The most common value of beta is 1: this is the F_1 score (aka balanced F-score). It weights precision and
            recall evenly. Values of beta greater than 1 weight recall higher than precision and less than 1 weights
            precision higher than recall.

            See
                https://en.wikipedia.org/wiki/F-score

        Args:
            x (BaseColumnExpression): an expression corresponding to the first series.
            y (BaseColumnExpression): an expression corresponding to the second series.
            beta (Optional[float]): the value of beta to use in the calculation (Defaults to 1.0).

        Returns:
            WindowAggregate: a WindowAggregate instance representing the F-score calculation.

        """
        return self._apply(x.metric.f_score(y, beta))
