"""
Search direction algorithms base class
"""
import abc
import numpy as np
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.algorithms.unidimensional import GoldenSection, MultimodalGoldenSection
from science_optimization.solvers import OptimizationResults
from science_optimization.algorithms.utils import hypercube_intersection
from science_optimization.algorithms.utils import box_constraints
from science_optimization.function import GenericFunction, BaseFunction
from science_optimization.problems import GenericProblem
from science_optimization.builder import OptimizationProblem
from typing import Tuple


class BaseSearchDirection(BaseAlgorithms):
    """Base class for search direction algorithms.

    """

    # attributes
    _x0 = None
    _x_bounds = None
    _uni_dimensional_opt_strategy = None
    _fun = None

    def __init__(self,
                 x0: np.ndarray,
                 n_max: int = None,
                 eps: float = None,
                 line_search_method: str='gs'):
        """Constructor of search direction algorithms.

        Args:
            x0                : (np.ndarray) initial point.
            n_max             : (int) maximum number of iterations.
            eps               : (float) maximum uncertainty for stop criterion.
            line_search_method: (str) line search strategy ('gs': golden section or 'mgs' multimodal gs).
        """

        self.x0 = 1.0 * x0
        self.uni_dimensional_opt_strategy = line_search_method
        if n_max is not None:
            self.n_max = n_max
        if eps is not None:
            self.eps = eps

    # attributes interface
    @property
    def x0(self):
        return self._x0

    @property
    def x_bounds(self):
        return self._x_bounds

    @property
    def uni_dimensional_opt_strategy(self):
        return self._uni_dimensional_opt_strategy

    @property
    def fun(self):
        return self._fun

    # setters
    @x0.setter
    def x0(self, x0):
        if x0.shape[1] == 1:
            self._x0 = x0
        else:
            raise ValueError("Initial point must be a column vector.")

    @x_bounds.setter
    def x_bounds(self, x_bounds):
        if x_bounds.shape[1] == 2:
            self._x_bounds = x_bounds
        else:
            raise ValueError("x_bounds must be a nx2-array.")

    @fun.setter
    def fun(self, fun):
        self._fun = fun

    @uni_dimensional_opt_strategy.setter
    def uni_dimensional_opt_strategy(self, uni_d_strategy):
        self._uni_dimensional_opt_strategy = uni_d_strategy

    def correct_direction_by_box(self, d: np.ndarray, x: np.ndarray, alpha):
        """
        check for values too near the box limits, and avoid the direction to go that way
        Args:
            d: current direction
            x: current x value
            alpha: previous value of alpha (unidimensional optimization)

        Returns:

        """

        for i, d_each in enumerate(d):

            if x[i] + d_each * alpha > self.x_bounds[i][1] + self.eps:
                d[i] = self.eps ** 2
                d = d / np.linalg.norm(d, 2)

            if x[i] + d_each * alpha < self.x_bounds[i][0] + self.eps:
                d[i] = self.eps ** 2
                d = d / np.linalg.norm(d, 2)

    # methods
    def optimize(self,
                 optimization_problem: OptimizationProblem,
                 debug: bool,
                 n_step: int=5):
        """Optimization core of Search direction methods.

        Args:
            optimization_problem: (OptimizationProblem) an optimization problem.
            debug               : (bool) debug option indicator.
            n_step              : (int) iterations steps to store optimization results.

        Returns:
            optimization_results: (OptimizationResults) optimization results.

        """

        # instantiate results
        optimization_results = OptimizationResults()
        optimization_results.message = 'Stop by maximum number of iterations.'

        # define functions
        self.fun = optimization_problem.objective.objectives

        # initial point
        x = self.x0

        # bounds
        self.x_bounds = np.hstack((optimization_problem.variables.x_min,
                                   optimization_problem.variables.x_max))

        # correct x to bounds
        x = box_constraints(x, self.x_bounds)

        # initial results
        nf = optimization_problem.objective.objectives.n_functions  # number of functions
        fx = np.zeros((nf, 0))
        optimization_results.x = np.zeros((x.shape[0], 0))

        # store parameters in debug option
        debug = False  # TODO(Matheus): debug
        if debug:
            optimization_results.parameter = {'alpha': np.zeros((0,))}

        alpha = 1

        # main loop
        stop = False
        while optimization_results.n_iterations < self.n_max and not stop:

            # compute search direction
            d = self._search_direction(fun=self.fun, x=x)
            self.correct_direction_by_box(d, x, alpha)

            # compute search interval
            interval = self._search_interval(x=x, d=d)

            # uni-dimensional optimization
            alpha, nfe = self._uni_dimensional_optimization(x=x, d=d, fun=self.fun, interval=interval,
                                                            strategy=self.uni_dimensional_opt_strategy, debug=debug)
            if debug:
                alpha = alpha[:, -1]

            # update function evaluation count
            optimization_results.n_function_evaluations += nfe

            # step towards search direction
            y = x + alpha*d
            fx_x = self.fun.eval(x)
            fx_y = self.fun.eval(y)

            # stop criteria: stalled
            if np.linalg.norm(x-y, 2) < self.eps:
                optimization_results.message = 'Stop by stalled search.'
                stop = True

            # stop criteria: unchanged function value
            if np.abs(fx_x - fx_y) < self.eps:
                optimization_results.message = 'Stop by unchanged function value.'
                stop = True

            # stop criteria: null gradient
            if np.linalg.norm(self.fun.gradient(y), 2) < self.eps:
                optimization_results.message = 'Stop by null gradient.'
                stop = True

            # update x
            x = y.copy()
            fx_x = fx_y.copy()

            # update results
            if debug and not (optimization_results.n_iterations + 1) % n_step:
                optimization_results.x = np.hstack((optimization_results.x, x))
                fx = np.hstack((fx, fx_x))
                optimization_results.fx = fx
                optimization_results.parameter['alpha'] = np.hstack((optimization_results.parameter['alpha'],
                                                                     np.array(alpha)))
            if not debug:
                optimization_results.x = x
                optimization_results.fx = fx_x

            # update count
            optimization_results.n_iterations += 1

        return optimization_results

    @abc.abstractmethod
    def _search_direction(self, **kwargs) -> np.ndarray:
        """Abstract search direction."""
        pass

    @staticmethod
    def _uni_dimensional_optimization(x: np.ndarray,
                                      d: np.ndarray,
                                      fun: BaseFunction,
                                      interval: list,
                                      strategy: str,
                                      debug: bool) -> Tuple[np.ndarray, int]:
        """Unidimensional optimization.

        Args:
            x       : (np.ndarray) current point.
            d       : (np.ndarray) search direction.
            fun     : (BaseFunction) function object.
            interval: (list) interval of search [a, b].
            strategy: (str) which uni-dimensional strategy to use.
            debug   : (bool) debug option indicator.

        Returns:
            alpha: optimal step
            nfe  : number of function evaluations
        """

        # objective function
        def line_search_function(a):
            return fun.eval(x + a*d)

        # function encapsulation
        f = [GenericFunction(func=line_search_function, n=1)]
        interval = np.array(interval).reshape(1, -1)

        # build problem
        op = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=interval))

        # instantiate uni-dimensional optimization class
        if strategy == "gs":
            op_result = GoldenSection()
        elif strategy == 'mgs':
            op_result = MultimodalGoldenSection(all_minima=False)
        else:
            raise Warning("Unknown unidimensional optimization strategy.")

        # optimize
        output = op_result.optimize(optimization_problem=op, debug=debug)
        alpha = output.x
        nfe = output.n_function_evaluations

        return alpha, nfe

    def _search_interval(self, x: np.ndarray, d: np.ndarray) -> list:
        """Determination of search interval.

        Args:
            x: (np.ndarray) current point.
            d: (np.ndarray) search direction.

        Returns:
            interval: (list) [a, b] search interval.

        """

        # interval
        a = 0
        if np.linalg.norm(d) < self.eps:
            b = a
        else:
            b, _ = hypercube_intersection(x=x, d=d, x_bounds=self.x_bounds)  # maximum step
        interval = [a, b]

        return interval
