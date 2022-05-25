"""
Linear solver of scipy package (base class)
"""
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.solvers import OptimizationResults
from science_optimization.function import LinearFunction
from science_optimization.builder import OptimizationProblem
from scipy.optimize import linprog
import numpy as np


class ScipyBaseLinear(BaseAlgorithms):
    """Base scipy linear method.

    """

    # parameters
    _method = None

    def __init__(self, method=None, n_max=None):
        """Constructor.

        Args:
            method: 'simplex' or 'interior-point'.
            n_max: maximum number of iterations.
        """

        if n_max is not None:
            self.n_max = n_max
        if method is not None:
            self.method = method

    # get
    @property
    def method(self):
        """Gets method."""
        return self._method

    # sets
    @method.setter
    def method(self, method):
        """Sets method."""

        if method == 'simplex' or method == 'interior-point':
            self._method = method
        else:
            raise ValueError("method must be either 'simplex' or 'interior-point'!")

    # optimize method
    def optimize(self,
                 optimization_problem: OptimizationProblem,
                 debug: bool,
                 n_step: int) -> OptimizationResults:
        """Optimization core.

           Args:
               optimization_problem: (OptimizationProblem) an optimization problem.
               debug               : (bool) debug option indicator.
               n_step              : (int) iterations steps to store optimization results.

           Returns:
               optimization_results: (OptimizationResults) optimization results.

        """

        # optimization problem check
        self.input(optimization_problem)

        # get input arguments
        _, _, c, d, _, _, A, b, Aeq, beq, x_min, x_max, _ = optimization_problem.op_arguments()

        # output
        optimization_results = OptimizationResults()
        output = linprog(c.ravel(), method=self.method, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                         bounds=np.hstack((x_min, x_max)), options={'maxiter': self.n_max})
        optimization_results.x = output.x.reshape(-1, 1) if isinstance(output.x, np.ndarray) else output.x
        optimization_results.fx = output.fun
        optimization_results.message = output.message
        optimization_results.n_iterations = output.nit

        return optimization_results

    @staticmethod
    def input(op: OptimizationProblem):
        """Optimization problem input.

        Args:
            op: (OptimizationProblem) an optimization problem instance.

        """

        # number of functions test
        if op.objective.objectives.n_functions > 1:
            raise ValueError('Not yet implemented multiobjective linear programming.')

        # linear objective function test
        if not isinstance(op.objective.objectives.functions[0], LinearFunction):
            raise ValueError('Objective function must be linear!')

        if op.nonlinear_functions_indices(op.constraints.inequality_constraints.functions) \
                or op.nonlinear_functions_indices(op.constraints.equality_constraints.functions):
            raise ValueError('Constraints must be linear.')
