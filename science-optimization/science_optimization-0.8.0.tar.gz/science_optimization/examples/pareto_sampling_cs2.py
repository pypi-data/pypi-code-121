"""
Toy problem for the 3 objective sampler (hybrid of Epsilon and NonDominated
"""
import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import QuadraticFunction
from science_optimization.solvers.pareto_samplers import EpsilonSampler
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
    c3 = np.array([[2], [-2]])
    d3 = np.array([2])

    # objectives
    f1 = QuadraticFunction(Q=Q, c=c1, d=d1)
    f2 = QuadraticFunction(Q=Q, c=c2, d=d2)
    f3 = QuadraticFunction(Q=Q, c=c3, d=d3)
    f = [f1, f3, f2]

    # constraints
    ineq_cons = []
    eq_cons = []

    # bounds
    x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
    x_max = np.array([5, 5]).reshape(-1, 1)  # upper
    x_lim = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

    # builder pareto sampler
    sampler = EpsilonSampler(optimization_problem=generic, n_samples=18, n_layers=3)
    results = sampler.sample()

    results.info()

    # contour plot of functions and solutions (variables and objective space)
    generic.plot()


if __name__ == "__main__":
    # run example
    pareto_sampling_cs2()
