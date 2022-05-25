"""
Optimization variables
"""
import numpy as np
from typing import List


class Variable:
    """Class for optimization variables.

    """

    # attributes
    _x_min = None  # variables
    _x_max = None  # variables
    _x_type = None  # variables' type

    def __init__(self, x_min: np.ndarray, x_max: np.ndarray, x_type: List[str]=None):
        """Constructor of variables.

        Args:
            x_min : (np.ndarray) (n x 1)-array with lower bounds.
            x_max : (np.ndarray) (n x 1)-array with upper bounds.
            x_type: (np.ndarray) (n x 1)-list with variables' type ('c': continuous or 'd': discrete).

        """

        # set bounds
        self.x_min = x_min
        self.x_max = x_max
        self.x_type = x_type

    # getters
    @property
    def x_min(self):
        return self._x_min

    @property
    def x_max(self):
        return self._x_max

    @property
    def x_type(self):
        return self._x_type

    # setters
    @x_min.setter
    def x_min(self, x_lb):
        """Setter of x_min.
        
        Args:
            x_lb: (n x 1)-numpy array

        """

        # check numpy
        if not isinstance(x_lb, np.ndarray):
            raise ValueError("x_min must be a numpy array!")

        # check dimension
        if not x_lb.shape[1]:
            raise ValueError("x_min must be a (n x 1)-numpy array!")

        # check consistency
        if self._x_min is not None:
            n = self._x_min.shape[0]
            if n != x_lb.shape[0] and n > 0:
                raise ValueError("x_min must be a ({} x 1)-numpy array!".format(n))
        # set
        self._x_min = x_lb

    @x_max.setter
    def x_max(self, x_ub):
        """Setter of x_max.

        Args:
            x_ub: (n x 1)-numpy array

        """

        # check numpy
        if not isinstance(x_ub, np.ndarray):
            raise ValueError("x_max must be a numpy array!")

        # check dimension
        if not x_ub.shape[1]:
            raise ValueError("x_max must be a (n x 1)-numpy array!")

        # check dimension consistency
        n = self._x_min.shape[0]
        if n != x_ub.shape[0] and n > 0:
            raise ValueError("x_max must be a ({} x 1)-numpy array!".format(n))

        # check range consistency
        if np.any((x_ub - self._x_min) < 0):
            raise ValueError("x_max must be greater than or equal x_min!")

        # set
        self._x_max = x_ub

    @x_type.setter
    def x_type(self, x_type):
        """Setter of x_min.

        Args:
            x_type: (n )-list

        """

        if x_type is not None:

            # check numpy
            if not isinstance(x_type, list):
                raise ValueError("x_type must be a list!")

            # check consistency
            n = self._x_min.shape[0]
            if n != len(x_type) and n > 0:
                raise ValueError("x_type must be a list of {} elements!".format(n))

            # check values
            if (x_type.count('c') + x_type.count('d')) != n:
                raise ValueError("x_type must be either 'c' or 'd'.")

            self._x_type = x_type

        else:
            self.x_type = ['c'] * self.x_min.shape[0]

    def dimension(self):
        """Return variable dimension."""
        return self.x_min.shape[0]
