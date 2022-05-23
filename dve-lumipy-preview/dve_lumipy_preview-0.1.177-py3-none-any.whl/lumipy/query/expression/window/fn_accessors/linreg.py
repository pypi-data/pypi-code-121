from .base import BaseWindowFunctionAccessor
from ...column.column_base import BaseColumnExpression


class LinregWindowFunctionAccessor(BaseWindowFunctionAccessor):
    """LinregWindowFunctionAccessor contains a collection of linear regression functions that act on a pair of column
    expressions in a given window such as alpha (intercept) and beta (gradient), as well as their respective standard
    errors.

    This and the other accessor classes behave like a namespace and keep the different window methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-dt

    Try hitting tab to see what functions you can use.
    """

    def alpha(self, x: BaseColumnExpression, y: BaseColumnExpression):
        """Apply an alpha calculation for a simple linear regression in this window to the given expressions.

        Notes:
            Alpha is the y intercept of the fitted line. See
                https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            x (BaseColumnExpression): an expression corresponding to the independent variable.
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the simple linear regression alpha
            calculation.
        """
        return self._apply(x.linreg.alpha(y))

    def beta(self, x: BaseColumnExpression, y: BaseColumnExpression):
        """Apply a beta calculation from a simple linear regression in this window to the given expressions.

        Notes:
            Beta is the gradient of the fitted line. See
                https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            x (BaseColumnExpression): an expression corresponding to the independent variable.
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the simple linear regression beta
            calculation.
        """
        return self._apply(x.linreg.beta(y))

    def alpha_std_err(self, x: BaseColumnExpression, y: BaseColumnExpression):
        """Apply an alpha standrd error calculation for a simple linear regression in this window to the given expressions.
        expression. This can be used to derive confidence intervals for the value of alpha.

        Notes:
            The calculation for the standard error of alpha assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            x (BaseColumnExpression): an expression corresponding to the independent variable.
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the standard error calculation
            for alpha.
        """
        return self._apply(x.linreg.alpha_std_err(y))

    def beta_std_err(self, x: BaseColumnExpression, y: BaseColumnExpression):
        """Apply a beta standard error calculation for a simple linear regression in this window to the given expressions.
        This can be used to derive confidence intervals for the value of beta.

        Notes:
            The calculation for the standard error of beta assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            x (BaseColumnExpression): an expression corresponding to the independent variable.
            y (BaseColumnExpression): an expression corresponding to the dependent variable.

        Returns:
            WindowAggregate: a WindowAggregate instance representing the standard error calculation
            for beta.
        """
        return self._apply(x.linreg.beta_std_err(y))
