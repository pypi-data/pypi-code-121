"""
Gradient algorithm
"""
import numpy as np
from science_optimization.algorithms.search_direction import BaseSearchDirection
from science_optimization.function import BaseFunction


class GradientAlgorithm(BaseSearchDirection):
    """Gradient algorithm

    """

    def _search_direction(self, fun: BaseFunction, x: np.ndarray) -> np.ndarray:
        """Search direction for gradient algorithm.

           Args:
               fun: function handler
               x  : point of evaluation

           Returns:
               d: normalized search direction

        """

        # search direction
        d = -fun.gradient(x)
        if np.linalg.norm(d) > self.eps:
            d = d / np.linalg.norm(d, 2)

        return d
