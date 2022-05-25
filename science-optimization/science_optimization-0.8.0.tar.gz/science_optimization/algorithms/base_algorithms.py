"""
Abstract class BaseAlgorithms
"""
import abc

from science_optimization.solvers import OptimizationResults


class BaseAlgorithms(metaclass=abc.ABCMeta):
    """Base class for algorithms family

    """

    # class attributes
    _eps = 1e-9  # uncertainty
    _n_max = 200  # maximum number of iterations

    @property
    def eps(self):
        return self._eps

    @property
    def n_max(self):
        return self._n_max

    @eps.setter
    def eps(self, epsilon):
        if epsilon >= 0:
            self._eps = epsilon
        else:
            raise ValueError("Epsilon cannot be negative!")

    @n_max.setter
    def n_max(self, n_max):
        if n_max >= 0:
            self._n_max = n_max
        else:
            raise ValueError("Maximum number of iterations cannot be negative!")

    @abc.abstractmethod
    def optimize(self, **kwargs) -> OptimizationResults:
        pass
