import numpy as np
from science_optimization.function import GenericFunction
from science_optimization.algorithms.search_direction import NewtonAlgorithm
from science_optimization.solvers import Optimizer
from science_optimization.problems import GenericProblem
from science_optimization.builder import OptimizationProblem


def generic_function_example():
    """Problem with a generic function"""

    # generic function
    def gen_function(x): return (x[0, :] - 4)**2 + (x[1, :] - 4)**2

    # generic function to base function
    f = [GenericFunction(func=gen_function, n=2)]

    # problem bounds
    x_min = np.array([-5, -10]).reshape(-1, 1)  # lower bound
    x_max = np.array([5, 10]).reshape(-1, 1)  # upper bound
    x_bounds = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=x_bounds))

    # builder optimization
    x0 = np.array([[0.0], [1.5]])
    optimizer = Optimizer(opt_problem=generic, algorithm=NewtonAlgorithm(x0=x0))
    results = optimizer.optimize(debug=False)

    # result
    results.info()


if __name__ == "__main__":
    # run example
    generic_function_example()
