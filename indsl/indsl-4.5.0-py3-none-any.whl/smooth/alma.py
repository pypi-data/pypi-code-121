# Copyright 2021 Cognite AS
from typing import List

import numpy as np
import pandas as pd

from ..exceptions import UserValueError
from ..type_check import check_types


@check_types
def alma(data: pd.Series, window: int = 10, sigma: float = 6, offset_factor: float = 0.75):
    """Arnaud Legoux moving average

    Moving average typically used in the financial industry which aims to strike a good balance between smoothness
    and responsivness (i.e. capture a general smoothed trend without allowing for significant lag). It can be
    interpreted as a Gaussian weighted moving average with an offset, where the offset, spread and window size are
    user defined.

    Args:
        data: Time series.
        window: Window size.
            Defaults to 10 data points or time steps for uniformly sample time series.
        sigma: Sigma.
            Parameter that controls the width of the Gaussian filter. Defaults to 6.
        offset_factor: Offset factor.
            Parameter that controls the magnitude of the weights for each past observation within the window.
            Defaults to 0.75.

    Returns:
        pandas.Series: Smoothed data.
    """
    # TODO : Refactor to accept TIME window instead of number of data points

    # Check data
    if len(data) <= window:
        raise RuntimeError(f"Not enough data to perform calculation. Expected {window} but got {len(data)}")

    # Check inputs
    if window == sigma == 0:
        raise UserValueError(
            "window or sigma can't be zero. Please change these user defined values to positive values."
        )

    # Calculate weights
    offset = int(offset_factor * window)
    k = np.array(range(0, window))
    weights = np.exp(-((k - offset) ** 2) / (sigma**2))

    # Apply smoothing function
    res = data.rolling(window=window).apply(lambda x: calculate_alma(x, weights))

    return res.dropna()


def calculate_alma(values: List, weights: np.ndarray):
    """Calculate alma value for a window time.

    Args:
        values: Datapoints in the window time.
        weights: Weights to calculate Alma value.

    Returns:
        float: Calculated Alma value.
    """
    weighted_sum = weights * values
    alma = weighted_sum.sum() / weights.sum()
    return alma
