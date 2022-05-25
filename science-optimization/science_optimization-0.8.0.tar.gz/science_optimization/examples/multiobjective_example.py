import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import QuadraticFunction
from science_optimization.solvers import Optimizer
from science_optimization.problems import GenericProblem
from science_optimization.algorithms.cutting_plane import EllipsoidMethod


def multiobjective_example():
    """Multiobjective problem example.

    """

    # objective functions
    xf = np.array([1, 1, 1]).reshape(-1, 1)
    Af = 2 * np.identity(3)
    bf = -np.matmul(Af, xf)
    cf = .5 * np.matmul(np.transpose(xf), np.matmul(Af, xf))
    xf2 = np.array([-1, -1, -1]).reshape(-1, 1)
    Af2 = np.diag([1, 2, 4])
    bf2 = -np.matmul(Af2, xf2)
    cf2 = .5 * np.matmul(np.transpose(xf2), np.matmul(Af2, xf2))
    f = [QuadraticFunction(Q=.5*Af, c=bf, d=cf), QuadraticFunction(Q=.5*Af2, c=bf2, d=cf2)]

    # inequality constraints
    Ag = 2 * np.identity(3)
    bg = np.zeros((3, 1))
    cg = -1
    xg2 = np.array([1, 1, 1]).reshape(-1, 1)
    Ag2 = 2 * np.identity(3)
    bg2 = -np.matmul(Ag2, xg2)
    cg2 = .5 * np.matmul(np.transpose(xg2), np.matmul(Ag2, xg2)) - 1
    ineq_cons = [QuadraticFunction(Q=.5*Ag, c=bg, d=cg), QuadraticFunction(Q=.5*Ag2, c=bg2, d=cg2)]

    # equality constraints
    eq_cons = []

    # bounds
    x_min = np.array([-10, -10, -10]).reshape(-1, 1)  # lower
    x_max = np.array([10, 10, 10]).reshape(-1, 1)  # upper
    x_lim = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

    # starting point
    x0 = np.array([20, 20, 20]).reshape(-1, 1)

    # cut option
    shallow_cut = 0

    # builder optimization
    optimizer = Optimizer(opt_problem=generic, algorithm=EllipsoidMethod(x0=x0, shallow_cut=shallow_cut))
    results = optimizer.optimize(debug=True, n_step=5)

    # result
    results.info()


if __name__ == "__main__":
    # run example
    multiobjective_example()
