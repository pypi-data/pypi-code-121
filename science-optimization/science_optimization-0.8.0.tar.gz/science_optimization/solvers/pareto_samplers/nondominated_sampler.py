"""
Non dominated sampler strategy
"""
from science_optimization.algorithms.cutting_plane import EllipsoidMethod
from science_optimization.solvers.pareto_samplers import BaseParetoSamplers
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem
from typing import Any
import numpy as np


class NonDominatedSampler(BaseParetoSamplers):
    """Nondominated Pareto front sampler."""

    # class attributes
    _distance_type = 0

    def __init__(self,
                 optimization_problem: OptimizationProblem,
                 algorithm: Any = None,
                 n_samples: int = None,
                 distance_type: int = None):
        """Constructor of optimizer class.

        Args:
            optimization_problem: (OptimizationProblem) optimization problem instance.
            algorithm           : (Any) an algorithm instance.
            n_samples           : (int) number os samples.
            distance_type       : (int) distance type calculation indicator (0: variables space, 1: objective space).
        """

        # instantiate super class
        super().__init__(optimization_problem, algorithm, n_samples)

        # parameters
        if distance_type is not None:
            self.distance_type = distance_type

    # getters
    @property
    def distance_type(self): return self._distance_type

    # setters
    @distance_type.setter
    def distance_type(self, dtype):
        if dtype == 0 or dtype == 1:
            self._distance_type = dtype
        else:
            raise ValueError('Type must be 0 or 1.')

    def sample_aux(self) -> OptimizationResults:
        """ Non-dominated sampler.

        Returns:
            output: (OptimizationResults) optimization results.
        """

        # vertices of pareto front
        x, fx, fxb = self.pareto_vertices()

        # sample
        for k in range(self.n_samples-2):

            # find non-dominated initial point
            fxn = np.zeros(fx.shape)
            for i in range(fx.shape[0]):  # normalization
                fxn[i, :] = (fx[i, :] - fxb[i, 0]) / (fxb[i, 1] - fxb[i, 0])

            # find connectivity
            e = self.pareto_connectivity(fxn)

            # i-th initial point
            xi = self.nd_initial(x, fxn, e)

            # optimize
            self.algorithm.x0 = xi  # set non-dominated initial point
            o = self.algorithm.optimize(optimization_problem=self.optimization_problem, debug=False)
            x = np.hstack((x, o.x))
            fx = np.hstack((fx, o.fx))

        # output
        output = OptimizationResults()
        output.x = x
        output.fx = fx

        return output

    def nd_initial(self, x, fx, e):
        """ Non-dominated initial point.

        Args:
            x : set of points in variables space.
            fx: set of points in objective space.
            e : edge connectivity.

        Returns:
            xi: non-dominated initial point.
        """

        # distance
        if self.distance_type == 0:
            d = np.sum((x[:, e[:, 0]] - x[:, e[:, 1]]) ** 2, axis=0)
        else:
            d = np.sum((fx[:, e[:, 0]] - fx[:, e[:, 1]]) ** 2, axis=0)

        # largest edge
        i = np.argmax(d)

        # mean point of largest segment
        xi = np.mean(x[:, e[i, :]], axis=1).reshape(-1, 1)

        return xi

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm):     # this sampler requires a multiobjective algorithm
        # verify instances
        if issubclass(type(algorithm), EllipsoidMethod):
            self._algorithm = algorithm
        else:
            raise Warning("Multiobjective algorithm not implemented yet!")
