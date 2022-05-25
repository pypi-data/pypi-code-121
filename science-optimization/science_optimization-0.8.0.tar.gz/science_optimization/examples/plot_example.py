import numpy as np
import matplotlib.pyplot as plt

from science_optimization.algorithms.lagrange import AugmentedLagrangian
from science_optimization.solvers import Optimizer
from science_optimization.solvers.pareto_samplers import NonDominatedSampler

from science_optimization.problems import GenericProblem

from science_optimization.builder import OptimizationProblem

from science_optimization.function import LinearFunction, QuadraticFunction


def plot_example():

    # Plot functions
    Q = np.array([[3, 0], [0, 1]])
    c = np.array([[8], [1]])
    d = 4

    # defining function object
    l_func = LinearFunction(c=c, d=d)
    q_func = QuadraticFunction(Q=Q, c=c, d=d)

    # plot function eval
    x_lim = np.array([[-5, 5], [-5, 5]])
    q_func.plot(x_lim)

    # _____________________________________________________
    # Plot mono objective optimization
    generic = OptimizationProblem(builder=GenericProblem(f=[q_func], eq_cons=[l_func], ineq_cons=[], x_bounds=x_lim))
    optimizer = Optimizer(
        opt_problem=generic,
        algorithm=AugmentedLagrangian(x0=np.array([[-4], [-4]]),
                                      eps=1e-6)
    )
    optimizer.optimize(debug=False)

    generic.plot()

    # ____________________________________________________
    # Plot pareto sample data
    f = [l_func, q_func]
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=x_lim))
    sampler = NonDominatedSampler(optimization_problem=generic)
    sampler.sample()

    generic.plot()


if __name__ == "__main__":
    # run problem example
    plot_example()
