"""
Toy problem for the random sampler (more than 3 objectives)
"""
import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import QuadraticFunction
from science_optimization.solvers.pareto_samplers import RandomSampler
from science_optimization.problems import GenericProblem


def pareto_sampling_cs2():
    """Multiobjective problem example, with 3 objectives

        Args:

    """

    # parameters objective function 1
    Q = np.array([[1, 0], [0, 1]])
    c1 = np.array([[0], [0]])
    d1 = np.array([0])

    # parameters objective function 2
    c2 = np.array([[-2], [-2]])
    d2 = np.array([2])

    # parameters objective function 3
    c3 = np.array([[2], [5]])
    d3 = np.array([2])

    # parameters objective function 4
    c4 = np.array([[4], [-3]])
    d4 = np.array([3])

    # parameters objective function 5
    Q5 = np.array([[3, 0], [0, 1]])
    c5 = np.array([[-2], [-8]])
    d5 = np.array([3])

    # objectives
    f1 = QuadraticFunction(Q=Q, c=c1, d=d1)
    f2 = QuadraticFunction(Q=Q, c=c2, d=d2)
    f3 = QuadraticFunction(Q=Q, c=c3, d=d3)
    f4 = QuadraticFunction(Q=Q, c=c4, d=d4)
    f5 = QuadraticFunction(Q=Q5, c=c5, d=d5)

    f = [f1, f3, f2, f4, f5]

    # constraints
    ineq_cons = []
    eq_cons = []

    # bounds
    x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
    x_max = np.array([7, 5]).reshape(-1, 1)  # upper
    x_lim = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

    # builder pareto sampler
    sampler = RandomSampler(optimization_problem=generic, n_samples=200)
    results = sampler.sample()

    results.info()

    # contour plot of functions and solutions (variables and objective space)
    generic.plot(levels=[1])


if __name__ == "__main__":
    # run example
    pareto_sampling_cs2()
