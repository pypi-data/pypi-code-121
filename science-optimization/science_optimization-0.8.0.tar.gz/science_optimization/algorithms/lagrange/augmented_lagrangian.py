"""
Augmented Lagrangian algorithm
"""
import numpy as np

from science_optimization.algorithms.derivative_free import NelderMead
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.algorithms.search_direction import QuasiNewton, GradientAlgorithm, NewtonAlgorithm
from science_optimization.builder import OptimizationProblem
from science_optimization.function.lagrange_function import AugmentedLagrangeFunction
from science_optimization.problems import GenericProblem
from science_optimization.solvers import OptimizationResults
from typing import Tuple, Any

class AugmentedLagrangian(BaseAlgorithms):
    """
    Augmented Lagrangian algorithm
    """

    def __init__(self,
                 x0: np.ndarray,
                 n_max: int = None,
                 eps: float = None,
                 randx: bool = False,
                 algorithm: Any = None,
                 c: float = 1.1):
        """Algorithm constructor.

        Args:
            x0   : (np.ndarray) initial point
            n_max: (int) maximum number of iterations for stop criterion
            eps  : (float) maximum uncertainty for stop criterion
            randx: (bool) True to use a different initial point in each Lagrangian iteration
            alg_choose: (int) chooses the method to solve the unconstrained problem
                              (0 -> Quasi Newton (BFGS) / 1 -> Gradient method / 2 -> Newton method / 3 -> Nelder Mead)
            c: (float) parameter used to update the rho value
        """

        # parameters
        self.x0 = x0
        if n_max is not None:
            self.n_max = n_max
        if eps is not None:
            self.eps = eps
        self.randx = randx

        if algorithm is not None:
            self.algorithm = algorithm
        else:
            self.algorithm = QuasiNewton(x0=x0)

        if c <= 1:
            raise Exception('Invalid value, must be greater than one')
        self.c = c

    # getters
    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm):
        # verify instances
       if issubclass(type(algorithm), QuasiNewton) or issubclass(type(algorithm), GradientAlgorithm) \
               or issubclass(type(algorithm), NewtonAlgorithm) or issubclass(type(algorithm), NelderMead):
            self._algorithm = algorithm
       else:
            raise Warning("Invalid algorithm, must solve constrained problems")

    def optimize(self, optimization_problem, debug=False, n_step=5):
        """Optimization core of Augmented Lagrangian method

        Args:
            optimization_problem: (OptimizationProblem) an optimization problem.
            debug               : (bool) debug option indicator.
            n_step              : (int) iterations steps to store optimization results.

        Returns:
            optimization_results: (OptimizationResults) optimization results.

        """
        optimization_results = OptimizationResults()
        optimization_results.message = 'Stop by maximum number of iterations.'

        f_obj = optimization_problem.objective.objectives
        x_bounds = np.hstack((optimization_problem.variables.x_min, optimization_problem.variables.x_max))

        n = len(optimization_problem.variables.x_type)

        h = optimization_problem.constraints.equality_constraints
        g = optimization_problem.constraints.inequality_constraints

        x0 = self.x0

        la_function = AugmentedLagrangeFunction(f_obj=f_obj, g=g, h=h, rho=1, c=self.c)

        # only parameter that changes through the iterations is f
        op_generic = OptimizationProblem(builder=GenericProblem(f=[la_function],
                                                                eq_cons=[], ineq_cons=[], x_bounds=x_bounds))
        stop_criteria = False
        k = 0
        prev_x = x0
        x_hist = np.array(x0)
        f_hist = [f_obj.eval(x0)]

        while k < self.n_max and not stop_criteria:

            self.algorithm.x0 = x0
            results = self.algorithm.optimize(optimization_problem=op_generic, debug=False)

            x_new = results.x

            if debug:
                x_hist = np.hstack((x_hist, x_new))
                f_hist.append(results.fx)

            # update Lagrange multipliers
            la_function.update_multipliers(x_new)

            k += 1

            if np.linalg.norm(x_new - prev_x) < self.eps:
                optimization_results.message = 'Stop by unchanged x value.'
                stop_criteria = True

            prev_x = x_new

            if self.randx:
                x0 = np.random.uniform(x_bounds[:, 0], x_bounds[:, 1], (1, n)).transpose()
            else:
                x0 = x_new

        if debug:
            optimization_results.x = x_hist
            optimization_results.fx = np.array(f_hist)

        else:
            optimization_results.x = prev_x
            optimization_results.fx = f_obj.eval(prev_x)

        optimization_results.n_iterations = k
        optimization_results.parameter = {'lambda': la_function.lag_eq, 'mu': la_function.lag_ineq}

        return optimization_results