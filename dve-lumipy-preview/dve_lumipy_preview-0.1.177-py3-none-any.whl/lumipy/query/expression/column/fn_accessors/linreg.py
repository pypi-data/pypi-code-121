from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.column_op.aggregation_op import (
    LinearRegressionAlpha, LinearRegressionBeta,
    LinearRegressionAlphaError, LinearRegressionBetaError
)


class LinregColumnFunctionAccessor:
    """LineregColumnFunctionAccessor contains a collection of linear regression functions that act on a column
    expression such as alpha (intercept) and beta (gradient), as well as their respective standard errors.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x: BaseColumnExpression):
        self._x = x

    def alpha(self, y: BaseColumnExpression) -> LinearRegressionAlpha:
        """Apply an alpha calculation for a simple linear regression to this expression and the input expression.

        Notes:
            Alpha is the y intercept of the fitted line. See https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            LinearRegressionAlpha: a LinearRegressionAlpha instance representing the simple linear regression alpha
            calculation.
        """
        return LinearRegressionAlpha(self._x, y)

    def beta(self, y: BaseColumnExpression) -> LinearRegressionBeta:
        """Apply a beta calculation from a simple linear regression to this expression and the input expression.

        Notes:
            Beta is the gradient of the fitted line. See https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            LinearRegressionBeta: a LinearRegressionBeta instance representing the simple linear regression beta
            calculation.
        """
        return LinearRegressionBeta(self._x, y)

    def alpha_std_err(self, y: BaseColumnExpression) -> LinearRegressionAlphaError:
        """Apply an alpha standrd error calculation for a simple linear regression to this expression and the input
        expression. This can be used to derive confidence intervals for the value of alpha.

        Notes:
            The calculation for the standard error of alpha assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            LinearRegressionAlphaError: a LinearRegressionAlphaError instance representing the standard error calculation
            for alpha.
        """
        return LinearRegressionAlphaError(self._x, y)

    def beta_std_err(self, y) -> LinearRegressionBetaError:
        """Apply a beta standard error calculation for a simple linear regression to this expression and the input
        This can be used to derive confidence intervals for the value of beta.

        Notes:
            The calculation for the standard error of beta assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            LinearRegressionBetaError: a LinearRegressionBetaError instance representing the standard error calculation
            for beta.
        """
        return LinearRegressionBetaError(self._x, y)
