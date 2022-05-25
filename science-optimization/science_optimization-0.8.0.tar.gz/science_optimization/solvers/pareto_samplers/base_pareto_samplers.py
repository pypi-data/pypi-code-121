"""
Base class for pareto sampler solvers
"""
import abc
from typing import Tuple, Any
import numpy as np
import copy

import science_optimization.function as sfunc
from science_optimization.algorithms.lagrange import AugmentedLagrangian
from science_optimization.algorithms.linear_programming import Glop
from science_optimization.builder import OptimizationProblem
from science_optimization.algorithms.cutting_plane import EllipsoidMethod


class BaseParetoSamplers(metaclass=abc.ABCMeta):
    """Base class for Pareto samplers algorithms."""

    # class attributes
    _n_samples = 9  # number of samples
    _algorithm = EllipsoidMethod(eps=1e-6)  # base algorithm for sampling a Pareto set
    _optimization_problem = None  # an optimization problem

    def __init__(self,
                 opt_problem: OptimizationProblem,
                 algorithm: Any = None,
                 n_samples: int = None):
        """Constructor of optimizer class.

        Args:
            opt_problem: (OptimizationProblem) optimization problem instance.
            algorithm  : (EllipsoidMethod) multiobjective algorithm.
            n_samples  : (int) number os samples.
        """

        self.optimization_problem = opt_problem
        if algorithm is not None:
            self.algorithm = algorithm
        if n_samples is not None:
            self.n_samples = n_samples

    # getters
    @property
    def n_samples(self):
        return self._n_samples

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def optimization_problem(self):
        return self._optimization_problem

    # setters
    @n_samples.setter
    def n_samples(self, n_samples):
        if n_samples >= 0:
            self._n_samples = n_samples
        else:
            raise ValueError("Number of samples cannot be negative!")

    @algorithm.setter
    def algorithm(self, algorithm):
        # verify instances
        if issubclass(type(algorithm), EllipsoidMethod) or issubclass(type(algorithm), AugmentedLagrangian) or \
                issubclass(type(algorithm), Glop):
            self._algorithm = algorithm
        else:
            raise Warning("Invalid algorithm, must solve constrained problems")

    @optimization_problem.setter
    def optimization_problem(self, opt_problem):
        if isinstance(opt_problem, OptimizationProblem):
            self._optimization_problem = opt_problem

    @abc.abstractmethod
    def sample_aux(self, **kwargs):
        pass

    def sample(self, **kwargs):

        results = self.sample_aux(**kwargs)

        self.optimization_problem.results_ = results
        return results

    def pareto_vertices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Find pareto vertices of a multiobjective problem.

        Returns:
            x : (np.ndarray) (n x o)-matrix with vertices in variable space.
            fx: (np.ndarray) (o x o)-matrix with vertices in objective space.
            fx_bounds: (np.ndarray) (o x 2)-matrix with min/max values of each objective on other vertices.

        """

        # cardinalities
        o = self.optimization_problem.objective.objectives.n_functions  # number of objectives
        n = self.optimization_problem.variables.x_min.shape[0]  # number of variables

        original_obj = self.optimization_problem.objective.objectives

        # initialize output
        x = np.zeros((n, o))
        fx = np.zeros((o, o))

        # solve mono objective problems
        op = copy.deepcopy(self.optimization_problem)

        for i in range(o):

            op.objective.objectives.clear()

            k = 1e-6        # tolerance used

            if original_obj.is_linear():

                c_mono = 1.0 * original_obj.functions[i].parameters['c']
                d_mono = 1.0 * original_obj.functions[i].parameters['d']

                for i2 in range(o):

                    if i2 != i:
                        c_mono += k * original_obj.functions[i2].parameters['c']
                        d_mono += k * original_obj.functions[i2].parameters['d']

                f_mono = sfunc.LinearFunction(c=c_mono,d=d_mono)

            else:
                w_eps = sfunc.LinearFunction(c=np.zeros((n, 1)), d=k)
                # set mono objective problem
                f_mono = self.optimization_problem.objective.objectives.functions[i]
                for i2 in range(o):

                    if i2 != i:
                        f_mono += w_eps * self.optimization_problem.objective.objectives.functions[i2]

            op.objective.objectives.add(f_mono)

            # mono objective problem solution
            mono = self.algorithm.optimize(optimization_problem=op, debug=False)
            x[:, i] = mono.x.ravel()

            # evaluate objectives at mono-objective solutions
            fx[:, i] = self.optimization_problem.objective.objectives.eval(x=mono.x).ravel()

        # bounds values of each objective
        fx_bounds = np.zeros((o, 2))
        fx_bounds[:, 0] = np.amin(fx, axis=1)
        fx_bounds[:, 1] = np.amax(fx, axis=1)

        return x, fx, fx_bounds

    @staticmethod
    def pareto_connectivity(x: np.ndarray) -> np.ndarray:
        """Connectivity of Pareto set.

        Args:
            x: (np.ndarray) set of points.

        Returns:
            e: (np.ndarray) edge connectivity.
        """

        # cardinalities
        n, m = x.shape

        # find edge connectivity
        if n == 0 or m < 2:
            e = np.zeros((0, 2))
        elif n <= 2:
            # sort according to first component
            i = np.argsort(x[0, :])
            e = np.hstack((i[:-1].reshape(-1, 1), i[1:].reshape(-1, 1)))
        else:
            raise ValueError('Not yet supported more than 2 objective functions.')

        return e
