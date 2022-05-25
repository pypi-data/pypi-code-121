"""
Unidimensional algorithms base class
"""
import numpy as np
from science_optimization.algorithms import BaseAlgorithms


class BaseUnidimensional(BaseAlgorithms):
    """Golden section algorithm class.

    """

    def __init__(self, eps: float = None, n_max: int = None):
        """Constructor of unidimensional optimization.

        Args:
            eps  : (float) numerical precision.
            n_max: (int) maximum number of iterations.
        """

        if eps is not None:
            self.eps = eps
        if n_max is not None:
            self.n_max = n_max

    # optimize method
    def optimize(self, optimization_problem, debug, n_step):
        """Optimize method for golden section.

        Args:
            optimization_problem: optimization problem
            debug               : debug option indicator
            n_step              : iterations step to store optimization results

        Returns:
            optimization_results: an OptimizationResults instance with feasible solution

        """
        pass

    @staticmethod
    def input(optimization_problem):
        """Optimization problem input.

        Args:
            optimization_problem: an optimization problem instance

        Returns:
            f       : function evaluator
            interval: search interval
        """

        # function
        f = optimization_problem.objective.objectives.functions
        if len(f) > 1:
            raise ValueError('Not yet implemented multiobjective line search.')
        else:
            f = f[0]

        # search interval
        interval = np.c_[optimization_problem.variables.x_min, optimization_problem.variables.x_max]
        if interval.shape[0] > 1:
            raise ValueError('Algorithm admits only one search interval.')

        return f, interval
