import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import QuadraticFunction
from science_optimization.solvers.pareto_samplers import NonDominatedSampler, EpsilonSampler, LambdaSampler, MuSampler
from science_optimization.problems import GenericProblem
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def pareto_sampling_cs0(s):
    """Multiobjective problem example.

        Args:
            s: nondominated_sampler.

    """

    # parameters objective function 1
    Q = np.array([[1, 0], [0, 1]])
    c1 = np.array([[0], [0]])
    d1 = np.array([0])

    # parameters objective function 2
    c2 = np.array([[-2], [-2]])
    d2 = np.array([2])

    # objectives
    f1 = QuadraticFunction(Q=Q, c=c1, d=d1)
    f2 = QuadraticFunction(Q=Q, c=c2, d=d2)
    f = [f1, f2]

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
    if s == 0:
        sampler = EpsilonSampler(optimization_problem=generic)
    elif s == 1:
        sampler = NonDominatedSampler(optimization_problem=generic)
    elif s == 2:
        sampler = MuSampler(optimization_problem=generic)
    else:
        sampler = LambdaSampler(optimization_problem=generic)
    results = sampler.sample()

    # contour
    delta = 0.02
    x = np.arange(-5, 5, delta)
    y = np.arange(-5, 5, delta)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(1, -1), Y.reshape(1, -1)))
    f1eval = np.reshape(f1.eval(XY), X.shape)
    f2eval = np.reshape(f2.eval(XY), X.shape)

    # contour plot of individual functions
    fig, ax = plt.subplots()
    ax.contour(X, Y, f1eval, 17, colors='k', linewidths=.8)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')

    # contour plot of individual functions
    fig, ax = plt.subplots()
    ax.contour(X, Y, f2eval, 17, colors='k', linewidths=.8)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')

    # contour plot of functions and solution
    fig, ax = plt.subplots()
    ax.contour(X, Y, f1eval, 17, colors='k', linewidths=.8)
    ax.contour(X, Y, f2eval, 17, colors='r', linewidths=.8)
    plt.scatter(results.x[0, :], results.x[1, :], s=8)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')

    # pareto front plot
    plt.figure()
    plt.scatter(results.fx[0, :], results.fx[1, :], s=8)
    plt.xlabel(r'$f_1$')
    plt.ylabel(r'$f_2$')
    plt.show()


if __name__ == "__main__":
    # run example
    pareto_sampling_cs0(s=2)
