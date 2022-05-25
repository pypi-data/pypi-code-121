"""
Dual decomposition method
"""
import numpy as np
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.builder import OptimizationProblem
from science_optimization.problems import GenericProblem
from science_optimization.function import GenericFunction, FunctionsComposite
from science_optimization.solvers import OptimizationResults
from science_optimization.algorithms.unidimensional import GoldenSection
import copy


class DualDecomposition(BaseAlgorithms):
    """Dual decomposition method.

    """

    # attributes
    _x0 = None

    def __init__(self,
                 x0: np.ndarray=np.array([[]]).reshape(-1, 1),
                 n_max: int=None,
                 eps: float=None):
        """Dual decomposition method constructor.

        Args:
            x0   : (np.ndarray) initial point
            n_max: (int) maximum number of iterations for stop criterion
            eps  : (float) maximum uncertainty for stop criterion
        """

        # parameters
        self.x0 = 1.0 * x0
        if n_max is not None:
            self.n_max = n_max
        if eps is not None:
            self.eps = eps

    # getters
    @property
    def x0(self):
        return self._x0

    # setters
    @x0.setter
    def x0(self, x0):
        if x0.shape[1] == 1:
            self._x0 = x0
        else:
            raise ValueError("Initial point must be a column vector.")

    def optimize(self, optimization_problem, debug=False, n_step=5):
        """Optimization core of Decomposition method.

        Args:
            optimization_problem: (OptimizationProblem) an optimization problem.
            debug               : (bool) debug option indicator.
            n_step              : (int) iterations steps to store optimization results.

        Returns:
            optimization_results: (OptimizationResults) optimization results.

        """

        # optimization parameters
        f = optimization_problem.objective.objectives
        x_bounds = np.hstack((optimization_problem.variables.x_min, optimization_problem.variables.x_max))

        # check whether inequality of inequality
        if not optimization_problem.constraints.inequality_constraints.functions:
            g = optimization_problem.constraints.equality_constraints
            constraint_type = 1
        else:
            g = optimization_problem.constraints.inequality_constraints
            constraint_type = 0

        # instantiate sub-problem and its solver
        sp_solver = GoldenSection(eps=self.eps, n_max=int(self.n_max / 2))
        sp = OptimizationProblem(builder=GenericProblem(f=[GenericFunction(func=lambda: 1, n=1)],
                                                        eq_cons=[],
                                                        ineq_cons=[],
                                                        x_bounds=np.zeros((0, 2))))

        # solve master problem evaluator
        def f_master(n):
            return -self.master_eval(f=f, g=g, nu=n, x_bounds=x_bounds, op=sp, solver=sp_solver)[1]

        # master problem bounds (nu bounds)
        if constraint_type:
            # equality constraint
            x_bounds_master = np.array([[-self.eps**-1, self.eps**-1]])
        else:
            # inequality constraint
            x_bounds_master = np.array([[0, self.eps**-1]])

        # optimization parameters
        nu = 1.
        x = self.x0
        k = 0
        k_max = int(self.n_max / 10)
        stop = False

        # master problem and solver
        mp = OptimizationProblem(builder=GenericProblem(f=[GenericFunction(func=f_master, n=1)],
                                                        eq_cons=[],
                                                        ineq_cons=[],
                                                        x_bounds=x_bounds_master))

        # main loop
        mp_solver = GoldenSection(eps=self.eps, n_max=self.n_max)
        results = OptimizationResults()
        while not stop and k < k_max:

            # run algorithm
            output = mp_solver.optimize(optimization_problem=mp, debug=False)

            # new price (nu)
            nu_new = output.x
            nu_diff = np.abs(nu - nu_new)
            nu = copy.copy(nu_new)

            # evaluate master problem
            x, fx, gx = self.master_eval(f=f, g=g, nu=nu, x_bounds=x_bounds, op=sp, solver=sp_solver)

            # update nu: bounds of master problem
            h = 2
            x_lb = nu-h*np.abs(nu) if constraint_type else np.maximum(0, nu-h*np.abs(nu))
            x_bounds_master = np.array([[x_lb, nu+h*np.abs(nu)]])

            # update problem bounds
            mp.variables.x_min = x_bounds_master[:, 0].reshape(-1, 1)
            mp.variables.x_max = x_bounds_master[:, 1].reshape(-1, 1)

            # stop criteria
            stop = (np.abs(gx) < self.eps and constraint_type) or (np.abs(nu) < self.eps) or \
                   (np.diff(x_bounds_master) < self.eps) or (nu_diff < self.eps and k > 0)

            # update counter
            k += 1

        # output
        results.x = x
        results.fx = f.eval(x)
        results.parameter = {'nu': nu}
        results.n_iterations = k

        return results

    @staticmethod
    def master_eval(f: FunctionsComposite,
                    g: FunctionsComposite,
                    nu: float,
                    x_bounds: np.ndarray,
                    op: OptimizationProblem,
                    solver: GoldenSection):
        """ Evaluates master problem.

        Args:
            f       : (FunctionsComposite) objective functions.
            g       : (FunctionsComposite) constraints.
            nu      : (float) allocation factor.
            x_bounds: (np.ndarray) bounds.
            op      : (OptimizationProblem) optimization problem.
            solver  : (GoldenSection) algorithm solver

        Returns:
            x        : (np.ndarray) sub-problems' solution.
            fx_master: (np.ndarray) objective evaluation at x.
            gx       : (np.ndarray) constraint evaluation at x.

        """
        # build and solve sub-problems
        n = x_bounds.shape[0]  # number of variables
        x_out = np.zeros((n, 1))

        # build generic problem instance
        for i in range(f.n_functions):

            # sub-problem
            def f_i(x):
                y = np.zeros((n, 1))
                y[i, :] = x
                return f.functions[i].eval(y) + nu * g.functions[i].eval(y)

            # update problem objective
            op.objective.objectives.remove()
            op.objective.objectives.add(GenericFunction(func=f_i, n=1))

            # update problem bounds
            op.variables.x_min = x_bounds[i, 0].reshape(-1, 1)
            op.variables.x_max = x_bounds[i, 1].reshape(-1, 1)

            output = solver.optimize(optimization_problem=op, debug=False)
            x_out[i, 0] = output.x

        # master eval
        gx = g.eval(x_out, composition='series')
        fx_master = f.eval(x_out, composition='series') + nu * gx

        return x_out, fx_master, gx
