from science_optimization.builder import OptimizationProblem
from science_optimization.problems import MIP
from science_optimization.solvers.pareto_samplers import EpsilonSampler
from science_optimization.algorithms.linear_programming import Glop
import numpy as np


def lp_sampling():
    """Multiobjective linear problem."""

    # problem
    C = np.array([[3, 1], [-1, -2]])  # objectives
    A = np.array([[3, -1]])  # inequality constraints
    b = np.array([[6]])
    x_bounds = np.array([[0, 10], [0, 3]])

    # problem
    op = OptimizationProblem(builder=MIP(c=C, A=A, b=b, x_bounds=x_bounds))

    # printing info
    op.info()

    # builder optimization
    sampler = EpsilonSampler(optimization_problem=op, algorithm=Glop(), n_samples=9)
    results = sampler.sample()

    # result
    results.info()

    # plot
    op.plot()


if __name__ == "__main__":
    # run example
    lp_sampling()
