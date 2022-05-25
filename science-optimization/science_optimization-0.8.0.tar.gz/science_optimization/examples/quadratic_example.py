import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.problems import Quadratic
from science_optimization.solvers import Optimizer
from science_optimization.algorithms.search_direction import GradientAlgorithm
from science_optimization.profiling import profiling


@profiling
def quadratic_example(problem=1):
    """ Quadratic problem examples.

    Args:
        problem: indicator of quadratic optimization problem to be used.

    """

    # choose problem
    if problem == 1:
        # Problem: (x[0]-1)^2 + 4.0*x[1]^2
        Q = np.array([[1, 0], [0, 4]])
        c = np.array([-2, 0]).reshape(-1, 1)
        d = 1
    elif problem == 2:
        # Problem: x[0]^2 + 3.0*x[1]^2
        Q = np.array([[1, 0], [0, 3]])
        c = np.array([0, 0]).reshape(-1, 1)
        d = 0
    else:
        raise Warning("Undefined problem example.")

    # bounds
    x_min = np.array([-10, -10]).reshape(-1, 1)  # lower bound
    x_max = np.array([10, 10]).reshape(-1, 1)  # upper bound
    x_bounds = np.hstack((x_min, x_max))

    # builder quadratic problem instance
    quadratic = OptimizationProblem(builder=Quadratic(Q=Q, c=c, d=d, x_bounds=x_bounds))

    # builder optimization
    x0 = np.array([[3], [6]])
    optimizer = Optimizer(opt_problem=quadratic, algorithm=GradientAlgorithm(x0=x0, line_search_method='gs'))
    results = optimizer.optimize()

    # result
    results.info()


if __name__ == "__main__":
    # run problem example
    quadratic_example(problem=1)
