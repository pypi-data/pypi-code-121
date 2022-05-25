import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.function import QuadraticFunction
from science_optimization.function import GenericFunction
from science_optimization.solvers.pareto_samplers import NonDominatedSampler, EpsilonSampler, LambdaSampler, MuSampler
from science_optimization.problems import GenericProblem
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def pareto_sampling_cs1(s):
    """Multiobjective problem example.

        Args:
            s: nondominated_sampler.

    """

    # objective function 1
    def f_obj1(x): return np.max(np.abs(x * (.5 + 1e-2) - .5 * np.sin(x) * np.cos(x)), axis=0)

    # parameters objective function 2
    Q = np.array([[10, 9], [9, 10]])
    c = np.array([[-90], [-100]])
    d = np.array([250])

    # objectives
    f1 = GenericFunction(func=f_obj1, n=2)
    f2 = QuadraticFunction(Q=Q, c=c, d=d)
    f = [f1, f2]

    # constraints
    ineq_cons = []
    eq_cons = []

    # bounds
    x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
    x_max = np.array([10, 10]).reshape(-1, 1)  # upper
    x_lim = np.hstack((x_min, x_max))

    # build generic problem instance
    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

    # builder sampler
    if s == 0:
        sampler = EpsilonSampler(optimization_problem=generic, n_samples=13)
    elif s == 1:
        sampler = NonDominatedSampler(optimization_problem=generic, n_samples=13)
    elif s == 2:
        sampler = MuSampler(optimization_problem=generic, n_samples=13)
    else:
        sampler = LambdaSampler(optimization_problem=generic, n_samples=13)
    results = sampler.sample()

    # contour
    delta = 0.02
    x = np.arange(-5, 10, delta)
    y = np.arange(-5, 10, delta)
    X, Y = np.meshgrid(x, y)
    XY = np.vstack((X.reshape(1, -1), Y.reshape(1, -1)))
    f1eval = np.reshape(f_obj1(XY), X.shape)
    f2eval = np.reshape(f2.eval(XY), X.shape)

    # contour plot of individual functions
    fig, ax = plt.subplots()
    ax.contour(X, Y, f1eval, 17, colors='k', linewidths=.8)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')

    # contour plot of individual functions
    fig, ax = plt.subplots()
    ax.contour(X, Y, f2eval, 17, colors='k', linewidths=.8)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')

    # contour plot of functions and solution
    fig, ax = plt.subplots()
    ax.contour(X, Y, f1eval, 17, colors='k', linewidths=.8)
    ax.contour(X, Y, f2eval, 17, colors='r', linewidths=.8)
    plt.scatter(results.x[0, :], results.x[1, :], s=8)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
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
    s = 1
    pareto_sampling_cs1(s)
