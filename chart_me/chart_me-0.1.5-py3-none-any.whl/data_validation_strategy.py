"""Defines ValidateColumnStrategy Prototal & Defines a Default Implementation

The Protocol specifies 1 method - validate_column.
The default implementation leverage module level Custom Exceptions

    Typical usage example:

    for c in cols:
            #will raise an error if insufficient
            ValidateColumnStrategyDefault.validate_column_strategy(df, c).validate_column() # noqa: E501
"""
# Standard library imports
import sys

if sys.version_info >= (3, 8):
    # Standard library imports
    from typing import Protocol
else:
    from typing_extensions import Protocol

# Third party imports
import pandas as pd

# chart_me imports
from chart_me.errors import (
    ColumnAllNullError,
    ColumnDoesNotExistsError,
    ColumnTooManyNullsError,
)


class ValidateColumnStrategy(Protocol):
    """Protocol Definition for ValidateColumnStrategy"""

    def validate_column(self) -> bool:
        """Only required method"""
        ...


class ValidateColumnStrategyDefault:
    """Default implentation of ValidateColumnStrategy

    Class is leverage to evaluate whether column selected is viable for charting

    Attributes:
        null_rate: A decimal indicating what percent of null entries in column is ok
    """

    null_rate: float = 0.95  # default check

    def __init__(self, df: pd.DataFrame, col: str, *, override_null_rate: float = 0.95):
        """Init of instance with ability to override class null_rate"""
        self.df = df
        self.col = col
        ValidateColumnStrategyDefault.null_rate = override_null_rate

    def validate_column(self) -> bool:
        """Logic the evaluate column

        Returns:
            True or Raises an Error #TODO think of better strategy

        Raises:
            ColumnDoesNotExistsError
            ColumnAllNullError
            ColumnTooManyNullsError
        """
        # check is exists
        try:
            _ = self.df[self.col]
        except KeyError:
            raise ColumnDoesNotExistsError(f"{self.col}")

        if self.df[self.col].isnull().all():
            raise ColumnAllNullError(f"{self.col}")

        if (
            self.df[self.col].isnull().sum() / len(self.col)
            > ValidateColumnStrategyDefault.null_rate
        ):
            raise ColumnTooManyNullsError(
                null_rate=ValidateColumnStrategyDefault.null_rate
            )

        return True
