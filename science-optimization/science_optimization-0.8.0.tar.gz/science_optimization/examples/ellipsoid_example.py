import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import LinearFunction
from science_optimization.function import QuadraticFunction
from science_optimization.solvers import Optimizer
from science_optimization.problems import GenericProblem
from science_optimization.algorithms.cutting_plane import EllipsoidMethod


def ellipsoid_example():
    """Ellipsoid problem example.

    """

    # objective function
    n = 3
    Q = np.eye(n)
    c = -2*np.array([3, 5, 40]).reshape(-1, 1)
    d = 3**2 + 5**2 + 40**2
    f = [QuadraticFunction(Q=Q, c=c, d=d)]

    # inequality constraints
    ineq_cons = [LinearFunction(c=np.array([1, 1, 0]).reshape(-1, 1), d=-10)]

    # equality constraints
    eq_cons = [LinearFunction(c=np.array([1, -1, 0]).reshape(-1, 1))]

    # bounds
    x_min = np.array([-10, -10, -10]).reshape(-1, 1)  # lower
    x_max = np.array([10, 10, 10]).reshape(-1, 1)  # upper
    x_lim = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

    # starting point
    x0 = np.array([0, 0, 0]).reshape(-1, 1)

    # cut option
    shallow_cut = 0

    # builder optimization
    optimizer = Optimizer(opt_problem=generic, algorithm=EllipsoidMethod(x0=x0, shallow_cut=shallow_cut))
    results = optimizer.optimize(debug=True)

    # result
    results.info()


if __name__ == "__main__":
    # run example
    ellipsoid_example()
