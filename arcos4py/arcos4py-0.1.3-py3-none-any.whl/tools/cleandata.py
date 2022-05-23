"""Module containing clipping and interpolation classes.

Example:
    >>> # Interpolation
    >>> from arcos4py.tools import interpolation
    >>> a = interpolation(data)
    >>> data_interp = a.interpolate()

    >>> # clipping
    >>> from arcos4py.tools import clipMeas
    >>> a = clipMeas(data)
    >>> data_clipped = a.clip(0.001, 0.999)

"""
import numpy as np
import pandas as pd


class interpolation:
    """Interpolate nan values in a numpy array.

    Attributes:
        data (DataFrame): Where NaN should be replaced with interpolated values.
    """

    def __init__(self, data: pd.DataFrame):
        """Interpolate nan values in a pandas dataframe.

        Uses pandas.interpolate with liner interpolation.

        Arguments:
            data (DataFrame): Where NaN should be replaced with interpolated values.
        """
        self.data = data

    def interpolate(self) -> pd.DataFrame:
        """Interpolate nan and missing values.

        Returns:
            DataFrame: Interpolated input data.
        """
        self.data = self.data.interpolate(axis=0)

        return self.data


class clipMeas:
    """Clip input array."""

    def __init__(self, data: np.ndarray) -> None:
        """Clips array to quantilles.

        Arguments:
            data (ndarray): To be clipped.
        """
        self.data = data

    def _calculate_percentile(self, data: np.ndarray, clip_low: float, clip_high: float):
        """Calculate upper and lower quantille.

        Arguments:
            data (ndarray): To calculate upper and lower quantile on.
            clip_low (float): Lower clipping boundary (quantile).
            clip_high (float): Upper clipping boundry (quantille).

        Returns:
            np.ndarray: Array with lower quantile and array with upper quantile.

        """
        quantille_low = np.quantile(data, clip_low, keepdims=True)
        quantille_high = np.quantile(data, clip_high, keepdims=True)
        return quantille_low, quantille_high

    def clip(self, clip_low: float = 0.001, clip_high: float = 0.999) -> np.ndarray:
        """Clip input array to upper and lower quantiles defined in clip_low and clip_high.

        Arguments:
            clip_low (float): Lower clipping boundary (quantile).
            clip_high (float): Upper clipping boundry (quantille).

        Returns:
            np.ndarray: A clipped array of the input data.
        """
        low, high = self._calculate_percentile(self.data, clip_low, clip_high)
        out = self.data.clip(low, high)
        return out
