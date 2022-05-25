import numpy as np

from science_optimization.solvers import Optimizer
from science_optimization.builder import OptimizationProblem
from science_optimization.function import GenericFunction
from science_optimization.problems import Quadratic, GenericProblem
from science_optimization.algorithms.derivative_free import NelderMead


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

    optimizer.algorithm.n_max = 2000

    results = optimizer.optimize(debug=False)

    # results.info()

    return results


def generate_points(x_min, x_max, dim, n=30):

    points = []

    for i in range(n):
        p = x_min + np.random.random_sample((dim, 1)) * (x_max - x_min)
        points.append(p)

    return points


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


def write_x0_result(dim, x0, fx, n_evals, stop_crit):
    with open(str(dim) + "_dim_x0_results.txt", "a+") as fp:
        fp.write(str(x0.T[0].tolist()) + "\t" + str(fx) + "\t" + str(n_evals) + stop_crit)
        fp.write("\n")


def write_dim_result(dim, fx_min, fx_median, fx_std, fx_max, n_evals_mean):

    with open("results.txt", "a+") as fp:
        fp.write(
            str(dim) + "\t" +
            str(fx_min) + "\t" +
            str(fx_median) + "\t" +
            str(fx_std) + "\t" +
            str(fx_max) + "\t" +
            str(n_evals_mean)
        )
        fp.write("\n")


def run_tests():

    for dim in range(11, 16):

        fx = []
        n_evals = []

        f, ineq_cons, eq_cons, x_min, x_max, x_lim = get_bm_1_problem(dim)

        initial_points = generate_points(x_min, x_max, dim, n=30)

        for p in range(len(initial_points)):
            x0 = initial_points[p].reshape(-1, 1)

            results = generic_fun(f, x0, x_lim, ineq_cons, eq_cons)

            n_evals.append(results.n_function_evaluations)
            fx.append(results.fx)

            with open(str(dim) + "_dim_x0_results.txt", "a+") as fp:
                fp.write(str(x0.T[0].tolist()) + "\t" + str(results.fx) + "\t" + str(results.n_function_evaluations))
                fp.write("\n")

            # print(x0.T[0].tolist(), results.fx, results.n_function_evaluations)

        fx = np.array(fx)
        n_evals = np.array(n_evals)

        n_data = [np.min(fx), np.median(fx), np.std(fx), np.max(fx), np.mean(n_evals)]

        with open("results.txt", "a+") as fp:
            fp.write(
                str(dim) + "\t" +
                str(np.min(fx)) + "\t" +
                str(np.median(fx)) + "\t" +
                str(np.std(fx)) + "\t" +
                str(np.max(fx)) + "\t" +
                str(np.mean(n_evals))
            )
            fp.write("\n")

        print(n_data)


if __name__ == "__main__":
    run_tests()
