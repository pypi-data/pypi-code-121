"""
Glop class (google's linear programming system)
"""
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.solvers import OptimizationResults
from science_optimization.function import LinearFunction
from science_optimization.builder import OptimizationProblem
from ortools.linear_solver import pywraplp
import numpy as np


class Glop(BaseAlgorithms):
    """Interface to Google GLOP solver (https://developers.google.com/optimization/install/)."""

    # parameters
    _t_max = None

    def __init__(self, t_max: float=5):
        """Constructor of glop optimization solver.

        Args:
            t_max: (float) time limit in seconds.
        """

        self.t_max = t_max

    # get
    @property
    def t_max(self):
        """Gets method."""
        return self._t_max

    # sets
    @t_max.setter
    def t_max(self, t_max):
        """Sets method."""

        self._t_max = int(t_max/1e3)

    # optimize method
    def optimize(self,
                 optimization_problem: OptimizationProblem,
                 debug: bool = False,
                 n_step: int = 0) -> OptimizationResults:
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
        _, _, c, d, _, _, A, b, Aeq, beq, x_min, x_max, x_type = optimization_problem.op_arguments()

        # instantiate solver object
        if 'd' in x_type:
            problem_type = 'MIP'
            problem_solver = pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
        else:
            problem_type = 'LP'
            problem_solver = pywraplp.Solver.GLOP_LINEAR_PROGRAMMING
        solver = pywraplp.Solver(problem_type, problem_solver)

        # create variables
        n = x_min.shape[0]
        x = []
        for i in range(n):
            if x_type[i] == 'c':
                x.append(solver.NumVar(float(x_min[i, 0]), float(x_max[i, 0]), "x_"+str(i)))
            elif x_type[i] == 'd':
                x.append(solver.IntVar(float(x_min[i, 0]), float(x_max[i, 0]), "x_"+str(i)))
            else:
                raise ValueError("Variable type must be either 'c' or 'd'.")

        # create inequality constraints (A*x <= b)
        mi = A.shape[0]
        ic = [[]] * mi
        for i in range(mi):
            ic[i] = solver.Constraint(-solver.infinity(), float(b[i, 0]))
            for j in range(n):
                ic[i].SetCoefficient(x[j], float(A[i, j]))

        # create equality constraints (Aeq*x = beq)
        me = Aeq.shape[0] if Aeq is not None else 0
        ec = [[]] * me
        for i in range(me):
            ec[i] = solver.Constraint(float(beq[i, 0]), float(beq[i, 0]))
            for j in range(n):
                ec[i].SetCoefficient(x[j], float(Aeq[i, j]))

        # set objective function
        objective = solver.Objective()
        for i in range(n):
            objective.SetCoefficient(x[i], float(c[0, i]))
        objective.SetMinimization()

        # set time limit
        solver.SetTimeLimit(self.t_max)

        # solver
        solver.Solve()

        # output
        op_results = OptimizationResults()
        xb = np.zeros((n, 1))
        for i in range(n):
            xb[i, 0] = x[i].solution_value()
        op_results.x = xb
        op_results.fx = np.array([solver.Objective().Value()])

        return op_results

    @staticmethod
    def input(op: OptimizationProblem):
        """Optimization problem input.

        Args:
            op: (OptimizationProblem)an optimization problem instance

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
