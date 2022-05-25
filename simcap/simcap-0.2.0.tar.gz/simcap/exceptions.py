# -*- coding: utf-8 -*-
"""
The :mod:`simcap.exceptions` module includes all custom warnings and error
classes used across simcap.
"""

__all__ = ["StationaryWarning", "CorrelatedExogWarning", "NegativeValuesError"]


class StationaryWarning(UserWarning):
    """
    Warning used to notify if a time series is stationary.
    """

    pass


class CorrelatedExogWarning(UserWarning):
    """
    Warning used when exogenous variables have been removed from the simulation
    due to high correlation with an endogenous variables.
    """

    pass


class NegativeValuesError(ValueError, AttributeError):
    """
    Exception to raise if series with negative values are being passed.
    """

    pass
