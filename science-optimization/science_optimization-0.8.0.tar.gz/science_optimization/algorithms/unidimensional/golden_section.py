"""
Golden section algorithm
"""
import numpy as np
from .base_unidimensional import BaseUnidimensional
from science_optimization.solvers import OptimizationResults
import nlpalg


class GoldenSection(BaseUnidimensional):
    """Golden section algorithm class.

    """

    # class attributes
    ratio = (np.sqrt(5)-1)/2  # golden ratio

    # optimize method
    def optimize(self, optimization_problem, debug, n_step=1):
        """Optimize method for golden section.

        Args:
            optimization_problem: optimization problem
            debug               : debug option indicator
            n_step              : iterations step to store optimization results

        Returns:
            optimization_results: an OptimizationResults instance with feasible solution

        """

        # parameters
        f, interval = self.input(optimization_problem=optimization_problem)

        # objective function
        def fgs(x):
            return f.eval(np.array([[x]]))

        # output
        alpha = nlpalg.goldensection(fgs, interval[0, 0], interval[0, 1], self.eps, self.n_max)
        f_alpha = f.eval(np.array([[alpha]]))

        # optimization
        opt_result = OptimizationResults()
        opt_result.x = alpha
        opt_result.fx = f_alpha

        return opt_result
