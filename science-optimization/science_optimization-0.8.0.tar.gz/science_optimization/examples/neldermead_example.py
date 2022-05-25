import numpy as np

from science_optimization.solvers import Optimizer
from science_optimization.builder import OptimizationProblem
from science_optimization.function import GenericFunction
from science_optimization.problems import Quadratic, GenericProblem
from science_optimization.algorithms.derivative_free import NelderMead


def generate_grid(x_min, x_max, n):

    coords = []

    for i in range(n):
        coords.append(np.arange(x_min[i][0], x_max[i][0]+1, 5))

    g = np.meshgrid(*coords)

    for i in range(n):
        coords[i] = g[i].reshape((np.prod(g[i].shape), )).reshape(-1, 1)

    return np.hstack(coords)


def quadratic(Q, c, d):

    # bounds
    x_min = np.array([-10, -10]).reshape(-1, 1)  # lower bound
    x_max = np.array([10, 10]).reshape(-1, 1)  # upper bound
    x_bounds = np.hstack((x_min, x_max))

    # builder quadratic problem instance
    quadratic = OptimizationProblem(builder=Quadratic(Q=Q, c=c, d=d, x_bounds=x_bounds))

    # builder optimization
    x0 = np.array([[5], [6]])

    delta_r = 1.0
    delta_e = 2.0
    delta_ic = 0.5
    delta_oc = 0.5
    delta_s = 0.5

    optimizer = Optimizer(
        opt_problem=quadratic,
        algorithm=NelderMead(x0, delta_r, delta_e, delta_ic, delta_oc, delta_s)
    )
    results = optimizer.optimize()

    # result
    results.info()


def generic_fun(f, x0, x_lim, ineq_cons, eq_cons):

    delta_r = 1.0
    delta_e = 2.0
    delta_ic = 0.5
    delta_oc = 0.5
    delta_s = 0.5

    generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

    optimizer = Optimizer(
        opt_problem=generic,
        algorithm=NelderMead(x0, delta_r, delta_e, delta_ic, delta_oc, delta_s)
    )

    optimizer.algorithm.n_max = 500

    results = optimizer.optimize(debug=True)

    results.info()

    return results


def get_bm_1_problem(n):

    def obj_func(x):
        a = [10 for i in range(n)]
        b = [100 for i in range(n)]

        s = 0

        for i in range(n):
            s += a[i] * np.abs(x[i][0] / b[i])

        return s

    def c_1(x):
        c = 4
        s = 0

        for i in range(n):
            s += np.power(x[i][0], 3)

        s -= c

        return s

    def c_2(x):
        d = 1 / np.pi
        s = 0

        for i in range(n):
            s += np.power(-1 + x[i][0], 2)

        s -= d

        return s

    def c_3(x):
        d = 3
        m = 100
        s = 0

        for i in range(n):
            s += x[i][0]

        s = d - m * np.sqrt(s)

        return s

    x_min = np.full((n, 1), -10)  # lower
    x_max = np.full((n, 1), 10)  # upper
    x_lim = np.hstack((x_min, x_max))

    f = [GenericFunction(func=obj_func, n=n)]

    ineq_cons = [
        GenericFunction(func=c_1, n=n),
        GenericFunction(func=c_2, n=n),
        GenericFunction(func=c_3, n=n)
    ]
    eq_cons = []

    return f, ineq_cons, eq_cons, x_min, x_max, x_lim


def get_bm_2_problem(n):

    def obj_func(x):

        s = 1

        for i in range(n):
            s *= x[i][0]

        s *= -1 * np.power(np.sqrt(n), n)

        return s

    def c_1(x):

        s = 0

        for i in range(n):
            s += x[i][0]

        return s - 1

    return obj_func, c_1


def get_bm_3_problem():

    def obj_func(x):

        s = np.sum(x[0:4, ])
        s -= np.sum(np.power(x[0:4, ], 2))
        s -= np.sum(x[4:13, ])

        return s

    def c_1(x):
        return 2*x[0][0] + 2*x[1][0] + x[9][0] + x[10][0] - 10

    def c_2(x):
        return 2*x[0][0] + 2*x[2][0] + x[9][0] + x[11][0] - 10

    def c_3(x):
        return 2*x[0][0] + 2*x[2][0] + x[10][0] + x[11][0] - 10

    def c_4(x):
        return -8 * x[0][0] + x[9][0]

    def c_5(x):
        return -8 * x[1][0] + x[10][0]

    def c_6(x):
        return -8 * x[2][0] + x[11][0]

    def c_7(x):
        return -2 * x[3][0] - x[4][0] + x[9][0]

    def c_8(x):
        return -2 * x[5][0] - x[6][0] + x[10][0]

    def c_9(x):
        return -2 * x[7][0] - x[8][0] + x[11][0]

    x_min = np.zeros((13, 1))
    x_max = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 100, 100, 1]).reshape(-1, 1)
    x_bounds = np.hstack((x_min, x_max))

    x0 = np.array([.5, .5, .5, .5, .5, .5, .5, .5, .5, 3, 3, 3, .5]).reshape(-1, 1)

    f = [GenericFunction(obj_func, 13)]
    ineq_cons = [
        GenericFunction(func=c_1, n=13),
        GenericFunction(func=c_2, n=13),
        GenericFunction(func=c_3, n=13),
        GenericFunction(func=c_4, n=13),
        GenericFunction(func=c_5, n=13),
        GenericFunction(func=c_6, n=13),
        GenericFunction(func=c_7, n=13),
        GenericFunction(func=c_8, n=13),
        GenericFunction(func=c_9, n=13)
    ]
    eq_cons = []

    return x0, x_bounds, f, ineq_cons, eq_cons


def get_bm_4_problem():

    def obj_func(x):

        a = np.sum(np.power(np.cos(x), 4))
        b = np.prod(np.power(np.cos(x), 2))
        c = np.sqrt(np.sum(np.arange(1, 21).reshape(-1, 1) * np.power(x, 2)))

        s = np.abs((a - 2*b)/c)

        return s

    def c_1(x):
        return 0.75 - np.prod(x)

    def c_2(x):
        return np.sum(x) - 7.5 * x.shape[0]

    x_min = np.zeros((20, 1))
    x_max = np.full((20, 1), 10)
    x_bounds = np.hstack((x_min, x_max))

    x0 = np.full((20, 1), 5)

    f = [GenericFunction(func=obj_func, n=20)]
    ineq_cons = [
        GenericFunction(func=c_1, n=20),
        GenericFunction(func=c_2, n=20)
    ]
    eq_cons = []

    return x0, x_bounds, f, ineq_cons, eq_cons


def get_bm_5_problem():

    def obj_func(x):
        return np.abs(np.power(x[0][0], 2) + np.power(x[1][0], 2)) + np.abs(np.sin(x[0][0])) + np.abs(np.cos(x[1][0]))

    def c_1(x):

        c = 4
        s = 0

        for i in range(2):
            s += np.power(x[i][0], 3)

        s -= c

        return s

    def c_2(x):

        d = 1 / np.pi
        s = 0

        for i in range(2):
            s += np.power(-1 + x[i][0], 2)

        s -= d

        return s

    def c_3(x):

        d = 3
        m = 100
        s = 0

        for i in range(2):
            s += x[i][0]

        s = d - m * np.sqrt(s)

        return s

    # bounds
    x_min = np.array([-10, -10]).reshape(-1, 1)  # lower
    x_max = np.array([10, 10]).reshape(-1, 1)  # upper
    x_lim = np.hstack((x_min, x_max))

    f = [GenericFunction(func=obj_func, n=2)]

    ineq_cons = [
        GenericFunction(func=c_1, n=2),
        GenericFunction(func=c_2, n=2),
        GenericFunction(func=c_3, n=2)
    ]
    eq_cons = []

    x0 = np.array([[5.0], [1.0]])

    return x0, x_lim, f, ineq_cons, eq_cons


def neldermead_example(problem=1):
    """

    Args:
        problem:

    Returns:

    """

    np.set_printoptions(precision=9, suppress=True)

    if problem == 1:
        # Problem: (x[0]-1)^2 + 4.0*x[1]^2
        Q = np.array([[1, 0], [0, 4]])
        c = np.array([-2, 0]).reshape(-1, 1)
        d = 1

        quadratic(Q, c, d)
    elif problem == 2:
        # Problem: x[0]^2 + 3.0*x[1]^2
        Q = np.array([[1, 0], [0, 3]])
        c = np.array([0, 0]).reshape(-1, 1)
        d = 0

        quadratic(Q, c, d)
    elif problem == 3:
        def f_obj(x): return np.max(np.abs(x * (.5 + 1e-2) - .5 * np.sin(x) * np.cos(x)), axis=0)

        # bounds
        x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
        x_max = np.array([10, 10]).reshape(-1, 1)  # upper
        x_lim = np.hstack((x_min, x_max))

        f = [GenericFunction(func=f_obj, n=2)]

        ineq_cons = []
        eq_cons = []

        x0 = np.array([[2], [2]])

        generic_fun(f, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 4:
        def f_obj(x): return x[0][0]*x[0][0] + x[1][0]*x[1][0] - x[0][0]*x[1][0]

        # bounds
        x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
        x_max = np.array([10, 10]).reshape(-1, 1)  # upper
        x_lim = np.hstack((x_min, x_max))

        f = [GenericFunction(func=f_obj, n=2)]

        ineq_cons = []
        eq_cons = []

        x0 = np.array([[2], [2]])

        generic_fun(f, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 5:
        def f_obj(x): return 200 * x[0][0]*x[0][0] + x[1][0]*x[1][0]

        # bounds
        x_min = np.array([-10, -10]).reshape(-1, 1)  # lower
        x_max = np.array([10, 10]).reshape(-1, 1)  # upper
        x_lim = np.hstack((x_min, x_max))

        f = [GenericFunction(func=f_obj, n=2)]

        ineq_cons = []
        eq_cons = []

        x0 = np.array([[10], [10]])

        generic_fun(f, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 6:
        def f_obj(x): return 100 * np.square((x[1][0] - np.square(x[0][0]))) + np.square(1 - x[0][0])

        # bounds
        x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
        x_max = np.array([10, 10]).reshape(-1, 1)  # upper
        x_lim = np.hstack((x_min, x_max))

        f = [GenericFunction(func=f_obj, n=2)]

        ineq_cons = []
        eq_cons = []

        x0 = np.array([[-2], [1]])

        generic_fun(f, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 7:
        def f_obj(x):
            return np.square(x[0][0] + 10 * x[1][0]) + 5 * np.square(x[2][0] - x[3][0]) + \
                   np.power((x[1][0] - 2 * x[2][0]), 4) + 10 * np.power(x[0][0] - x[3][0], 4)

        # bounds
        x_min = np.array([-5, -5, -5, -5]).reshape(-1, 1)  # lower
        x_max = np.array([10, 10, 10, 10]).reshape(-1, 1)  # upper
        x_lim = np.hstack((x_min, x_max))

        f = [GenericFunction(func=f_obj, n=4)]

        ineq_cons = []
        eq_cons = []

        x0 = np.array([[3], [-1], [0], [1]])

        generic_fun(f, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 8:

        n = 5

        f, ineq_cons, eq_cons, x_min, x_max, x_lim = get_bm_1_problem(n)

        x0 = np.full((n, 1), 1.0)

        generic_fun(f, x0, x_lim, ineq_cons, eq_cons)

    elif problem == 9:
        x0, x_lim, obj_func, ineq_cons, eq_cons = get_bm_3_problem()

        generic_fun(obj_func, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 10:
        x0, x_lim, obj_func, ineq_cons, eq_cons = get_bm_4_problem()

        generic_fun(obj_func, x0, x_lim, ineq_cons, eq_cons)
    elif problem == 11:
        x0, x_bounds, f, ineq_cons, eq_cons = get_bm_5_problem()

        generic_fun(f, x0, x_bounds, ineq_cons, eq_cons)
    else:
        raise Warning("Undefined problem example.")


if __name__ == '__main__':
    neldermead_example(problem=1)
