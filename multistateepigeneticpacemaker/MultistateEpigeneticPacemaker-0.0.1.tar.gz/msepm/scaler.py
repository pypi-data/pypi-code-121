import numpy as np


class ScalingError(Exception):
    """Error running scaler """
    pass


class Scaler:
    """Simple min, max scaler implementation for array with m samples and n features"""

    def __init__(self, X_min: np.ndarray = None, X_max: np.ndarray = None):
        """
        attributes:
            self.scale_X_min: np.ndarray = min scaling value of m rows
            self.scale_X_max: np.ndarray = max scaling value of m rows
            self.X_min: np.ndarray = min of m rows
            self.X_max: np.ndarray = max of m rows
        """
        self.scale_X_min = X_min
        self.scale_X_max = X_max
        self.X_min = None
        self.X_max = None

    def fit(self, X: np.ndarray):
        """Set min and max values"""
        self.X_min = np.min(X, axis=0)
        if self.scale_X_min is None:
            self.scale_X_min = self.X_min
        self.X_max = np.max(X, axis=0)
        if self.scale_X_max is None:
            self.scale_X_max = self.X_max

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Scale input array to reference distribution range"""
        if self.X_min is None:
            raise ScalingError("Must fit scaler before transforming")
        # Scale input value to 0 - 1
        X_std = (X - self.X_min) / (self.X_max - self.X_min)
        # Scale values to original reference range
        return X_std * (self.scale_X_max - self.scale_X_min) + self.scale_X_min

    def fit_transform(self, X: np.ndarray):
        self.fit(X)
        return self.transform(X)
