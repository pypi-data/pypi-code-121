"""
Newton algorithm
"""
import numpy as np
from .base_search_direction import BaseSearchDirection


class NewtonAlgorithm(BaseSearchDirection):
    """ Newton Algorithm

    """
    def _search_direction(self, fun, x):
        """Search direction for newton algorithm.

        Args:
            fun: function handler
            x  : point of evaluation

        Returns:
            d: normalized search direction

        """
        # search direction
        d = -np.dot(np.linalg.inv(fun.hessian(x)[0, :, :]), fun.gradient(x))
        d = d / np.linalg.norm(d, 2)

        return d
