import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import GenericFunction
from science_optimization.solvers import Optimizer
from science_optimization.problems import SeparableResourceAllocation
from science_optimization.algorithms.decomposition import DualDecomposition


def decomposition_example():
    """Decomposition problem example.

        Solve problem:

        min f_1(x_1) + f_2(x_2), f_i(x_i) = e^(-2*x_i)
        s.t. x_1 + x_2 - 10 <= 0
        2 <= x_i <= 6

    """

    # dimension
    n = 2

    # objective functions
    def f_1(x):
        return np.exp(-2*x[0, :]) + 0 * x[1, :]

    def f_2(x):
        return np.exp(-2*x[1, :]) + 0 * x[0, :]

    # inequality constraints functions
    def g_1(x):
        return x[0, :] - 10

    def g_2(x):
        return x[1, :]

    # input lists
    f_i = [GenericFunction(func=f_1, n=n), GenericFunction(func=f_2, n=n)]  # f_i list
    g_i = [GenericFunction(func=g_1, n=n), GenericFunction(func=g_2, n=n)]  # g_i list

    # bounds
    x_min = np.array([2, 2]).reshape(-1, 1)  # lower
    x_max = np.array([6, 6]).reshape(-1, 1)  # upper
    x_bounds = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=SeparableResourceAllocation(f_i=f_i,
                                                                      coupling_eq_constraints=[],
                                                                      coupling_ineq_constraints=g_i,
                                                                      x_bounds=x_bounds
                                                                      ))
    # starting point
    x0 = np.array([0, 0]).reshape(-1, 1)

    # builder optimization
    optimizer = Optimizer(opt_problem=generic, algorithm=DualDecomposition(x0=x0))
    results = optimizer.optimize()

    # result
    results.info()


if __name__ == "__main__":
    # run example
    decomposition_example()
