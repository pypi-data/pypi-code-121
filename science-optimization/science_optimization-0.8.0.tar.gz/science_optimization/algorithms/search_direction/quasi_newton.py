"""
Quasi Newton algorithm
"""
import numpy as np
from .base_search_direction import BaseSearchDirection


class QuasiNewton(BaseSearchDirection):
    """
    Quasi Newton Algorithm

    """

    def __init__(self,
                 x0: np.ndarray,
                 n_max: int=None,
                 eps: float=None,
                 line_search_method: str='gs',
                 rho: float=1,
                 theta: float=1):
        """
        Default initialization uses BFGS
        Args:
            x0                  : (np.ndarray) initial point.
            n_max               : (int) maximum number of iterations.
            eps                 : (float) maximum uncertainty for stop criterion.
            line_search_method  : (str) line search strategy ('gs': golden section or 'mgs' multimodal gs).
            rho                 : (float) quasi newton formula parameter
            theta               : (float) quasi newton formula parameter
        """

        super().__init__(x0, n_max, eps, line_search_method)
        self.B = np.eye(len(x0))    # inverse hessian approximation
        self.prev_x = None
        self.prev_g = None

        self.rho = rho
        self.theta = theta

    @property
    def x0(self):
        return self._x0

    @x0.setter
    def x0(self, x0):
        if x0.shape[1] == 1:
            self._x0 = x0
        else:
            raise ValueError("Initial point must be a column vector.")

        # each time x0 is reset, auxiliary variables are reinitialized
        self.B = np.eye(len(x0))
        self.prev_x = None
        self.prev_g = None

    def _search_direction(self, fun, x):
        """Search direction for quasi newton algorithm.

        Args:
            fun: function handler
            x  : point of evaluation

        Returns:
            d: normalized search direction

        """
        g = fun.gradient(x)
        if self.prev_x is not None:     # not first iteration
            y = g - self.prev_g
            p = x - self.prev_x

            v = (
                np.sqrt(np.dot(np.dot(y.transpose(), self.B), y)) *
                (
                    (
                            p / (np.dot(p.transpose(), y))
                    ) - (
                            np.dot(self.B, y) / (np.dot(np.dot(y.transpose(), self.B), y))
                    )
                )

            )

            self.B = (
                    (
                            self.B - (
                                np.dot(np.dot(np.dot(self.B, y), y.transpose()), self.B) /
                                np.dot(np.dot(y.transpose(), self.B), y)
                            ) + self.theta * np.dot(v, v.transpose())
                    ) * self.rho +
                    np.dot(p, p.transpose()) / np.dot(p.transpose(), y)
            )

        # updates previous values
        self.prev_x = x
        self.prev_g = g

        # search direction
        d = -np.dot(self.B, g)

        norm = np.linalg.norm(d, 2)
        if norm != 0:       # avoids error when evaluating points with gradient zero
            d = d / norm

        return d
