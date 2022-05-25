"""
Nelder-Mead simplex algorithm
"""

import copy
import numpy as np
from science_optimization.algorithms.utils import box_constraints
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem
from science_optimization.function import BaseFunction
from science_optimization.algorithms import BaseAlgorithms


class NelderMead(BaseAlgorithms):
    """
    Nelder-Mead simplex algorithm to minimize derivative-free non-linear functions.
    """

    # starting point
    _x0 = None
    _x_min = None
    _x_max = None
    _x_bounds = None

    _x_min_norm = None
    _x_max_norm = None

    # problem dimensio
    _dim = None

    # function
    _f = None

    # constraint
    _g = None

    # function values
    _fx = None
    _gx = None

    # algorithm constants
    _delta_r = None
    _delta_e = None
    _delta_ic = None
    _delta_oc = None
    _delta_s = None

    # simplex point lists
    _simplex = None

    def __init__(self, x0, delta_r=1.0, delta_e=2.0, delta_ic=0.5, delta_oc=0.5, delta_s=0.5):
        """

        Args:
            x0:
            delta_r:
            delta_e:
            delta_ic:
            delta_oc:
            delta_s:
        """

        self.x0 = x0
        self.dim = x0.shape[0]

        self.x_min_norm = np.zeros((self.dim, 1))
        self.x_max_norm = np.full((self.dim, 1), 100)

        self.delta_r = delta_r
        self.delta_e = delta_e
        self.delta_ic = delta_ic
        self.delta_oc = delta_oc
        self.delta_s = delta_s

        self.simplex = []

        self.fx = None
        self.gx = None
        self.x_min = None
        self.x_max = None
        self.x_bounds = None

    @property
    def x0(self):
        return self._x0

    @property
    def x_min(self):
        return self._x_min

    @property
    def x_max(self):
        return self._x_max

    @property
    def x_bounds(self):
        return self._x_bounds

    @property
    def x_min_norm(self):
        return self._x_min_norm

    @property
    def x_max_norm(self):
        return self._x_max_norm

    @property
    def dim(self):
        return self._dim

    @property
    def f(self):
        return self._f

    @property
    def g(self):
        return self._g

    @property
    def fx(self):
        return self._fx

    @property
    def gx(self):
        return self._gx

    @property
    def delta_r(self):
        return self._delta_r

    @property
    def delta_e(self):
        return self._delta_e

    @property
    def delta_ic(self):
        return self._delta_ic

    @property
    def delta_oc(self):
        return self._delta_oc

    @property
    def delta_s(self):
        return self._delta_s

    @property
    def simplex(self):
        return self._simplex

    @x0.setter
    def x0(self, value):
        self._x0 = value

    @x_min.setter
    def x_min(self, value):
        self._x_min = value

    @x_max.setter
    def x_max(self, value):
        self._x_max = value

    @x_bounds.setter
    def x_bounds(self, value):
        self._x_bounds = value

    @x_min_norm.setter
    def x_min_norm(self, value):
        self._x_min_norm = value

    @x_max_norm.setter
    def x_max_norm(self, value):
        self._x_max_norm = value

    @dim.setter
    def dim(self, value):
        self._dim = value

    @f.setter
    def f(self, value):

        if not isinstance(value, BaseFunction):
            raise Exception("The function must be an instance of BaseFunction!")

        self._f = value

    @g.setter
    def g(self, value):

        if not isinstance(value, BaseFunction):
            raise Exception("The function must be an instance of BaseFunction!")

        self._g = value

    @fx.setter
    def fx(self, value):
        self._fx = value

    @gx.setter
    def gx(self, value):
        self._gx = value

    @delta_r.setter
    def delta_r(self, value):
        self._delta_r = value

    @delta_e.setter
    def delta_e(self, value):
        self._delta_e = value

    @delta_ic.setter
    def delta_ic(self, value):
        self._delta_ic = value

    @delta_oc.setter
    def delta_oc(self, value):
        self._delta_oc = value

    @delta_s.setter
    def delta_s(self, value):
        self._delta_s = value

    @simplex.setter
    def simplex(self, value):
        self._simplex = value

    def initialize_fminsearch(self):
        """

        Args:
            dim:

        Returns:

        """

        simplex = [self.x0]

        for i in range(self.dim):
            e_i = np.eye(1, self.dim, i).reshape(self.dim, 1)
            h_i = 0.05 if self.x0[i][0] != 0 else 0.00025
            simplex.append(box_constraints(self.x0 + h_i * e_i, self.x_bounds))

        self.simplex = simplex

    def initialize_simplex_size(self, size):
        """

        Args:
            size:

        Returns:

        """

        dim = self.dim
        simplex = [self.x0]

        p = size / (dim * np.sqrt(2))
        p = p * ((np.sqrt(dim+1)) + dim - 1)

        q = size / (dim * np.sqrt(2))
        q = q * ((np.sqrt(dim + 1)) - 1)

        e = np.identity(dim)

        for i in range(1, dim+1):
            point_sum = np.zeros((dim, 1))
            p_sign = 1

            e[i - 1][i - 1] = 0

            for j in range(dim):
                if self.x0[j][0] > (self.x_min_norm[j][0] + self.x_max_norm[j][0]) / 2:
                    point_sum += -1 * q * e[:, j].reshape(dim, 1)
                else:
                    point_sum += q * e[:, j].reshape(dim, 1)

            e[i - 1][i - 1] = 1

            if self.x0[i - 1][0] > (self.x_min_norm[i - 1][0] + self.x_min_norm[i - 1][0]) / 2:
                p_sign = -1

            new_point = self.x0 + p_sign * p * e[i - 1].reshape(dim, 1) + point_sum

            simplex.append(new_point)

        self.simplex = simplex

    def centroid(self, xw_index):
        """

        Args:
            xw_index:

        Returns:

        """

        simplex = copy.deepcopy(self.simplex)
        del(simplex[xw_index])

        return np.mean(simplex, axis=0)

    def reflect(self, x_centroid, xw_index):
        """

        Args:
            x_centroid:

        Returns:

        """
        return x_centroid + self.delta_r * (x_centroid - self.simplex[xw_index])

    def expand(self, x_centroid, x_reflect):
        """

        Args:
            x_centroid:
            x_reflect:

        Returns:

        """

        return x_centroid + self.delta_e * (x_reflect - x_centroid)

    def inside_contraction(self, x_centroid, x_reflect):
        """

        Args:
            x_centroid:
            x_reflect:

        Returns:

        """
        return x_centroid - self.delta_ic * (x_reflect - x_centroid)

    def outside_contraction(self, x_centroid, x_reflect):
        """

        Args:
            x_centroid:
            x_reflect:

        Returns:

        """

        return x_centroid + self.delta_oc * (x_reflect - x_centroid)

    def shrink(self, x_best):
        """

        Args:
            x_best:

        Returns:

        """

        for j in range(1, len(self.simplex)):
            x_new = x_best + self.delta_s * (self.simplex[j] - x_best)
            fx_new, gx_new = self.eval_fg(self.norm2real(x_new))

            self.replace_point(idx=j, x=x_new, fx=fx_new, gx=gx_new)

    def box_feasible(self, x):
        """

        Args:
            x:

        Returns:

        """

        return not(any(np.less(x, self.x_min_norm)) or any(np.greater(x, self.x_max_norm)))

    @staticmethod
    def is_less_than(fx_1, gx_1, fx_2, gx_2):
        """

        Args:
            fx_1:
            gx_1:
            fx_2:
            gx_2:

        Returns:

        """

        if gx_1 > 0 and gx_2 > 0:
            return gx_1 < gx_2
        elif gx_1 <= 0 and gx_2 <= 0:
            return fx_1 < fx_2
        else:
            return gx_1 <= 0

    def norm2real(self, x_norm):
        """

        Args:
            x_norm:

        Returns:

        """

        x = 0.01 * x_norm
        x = (self.x_max - self.x_min) * x
        x = x + self.x_min

        return x

    def real2norm(self, x):
        """

        Args:
            x:

        Returns:

        """

        x_norm = (x - self.x_min) / (self.x_max - self.x_min)
        x_norm = x_norm * 100

        return x_norm

    def constraint_sum(self, x):
        """

        Args:
            x:

        Returns:

        """

        if self.g is not None:
            gx_eval = self.g.eval(x)

            return np.sum(gx_eval[np.where(gx_eval > self.eps)])
        else:
            return 0

    def eval_fg(self, x):
        """

        Args:
            x:

        Returns:

        """

        fx = self.f.eval(x)
        gx = self.constraint_sum(x=x)

        return fx, gx

    def replace_point(self, idx, x, fx, gx):
        """

        Args:
            idx:
            x:
            fx:
            gx:

        Returns:

        """

        self.simplex[idx] = x
        self.fx[idx] = fx
        self.gx[idx] = gx

    def min(self, x, y):
        """

        Args:
            x:
            y:

        Returns:

        """

        x_real = self.norm2real(x)
        y_real = self.norm2real(y)

        fx, gx = self.eval_fg(x_real)
        fy, gy = self.eval_fg(y_real)

        if self.is_less_than(fx, gx, fy, gy):
            return x

        return y

    def sort_simplex(self):
        """

        Returns:

        """

        index = [x for x in range(len(self.fx))]

        gx_fx_idx = [(x, y, z) for x, y, z in zip(self.gx, self.fx, index)]
        result = [t[2] for t in sorted(gx_fx_idx)]

        return result

    def optimize(self, optimization_problem, debug=False, n_step=10):
        """

        Args:
            optimization_problem:
            debug:
            n_step:

        Returns:

        """

        if not isinstance(optimization_problem, OptimizationProblem):
            raise Exception("Optimize must have and OptimizationProblem instance as argument!")

        if optimization_problem.objective.objectives.n_functions != 1:
            raise Exception("Method able to optimize only one function.")

        optimization_results = OptimizationResults()
        optimization_results.message = 'Stop by maximum number of iterations.'

        self.f = optimization_problem.objective.objectives.functions[0]

        if optimization_problem.has_inequality_constraints():
            self.g = optimization_problem.constraints.inequality_constraints

        self.x_min = optimization_problem.variables.x_min
        self.x_max = optimization_problem.variables.x_max

        self.x_bounds = np.hstack((optimization_problem.variables.x_min, optimization_problem.variables.x_max))

        self.x0 = box_constraints(self.x0, self.x_bounds)

        self.x0 = self.real2norm(self.x0)

        self.initialize_simplex_size(size=10)

        self.fx = np.array([self.f.eval(self.norm2real(x)) for x in self.simplex])
        optimization_results.n_function_evaluations += len(self.simplex)

        if self.g is not None:
            gx = []

            for x in self.simplex:
                gx.append(self.constraint_sum(x=self.norm2real(x)))

            self.gx = np.array(gx)
        else:
            self.gx = np.zeros(len(self.simplex))

        index = self.sort_simplex()

        b = index[0]
        s = index[-2]
        w = index[-1]

        stop = False

        while optimization_results.n_iterations < self.n_max and not stop:

            x_c = self.centroid(xw_index=w)

            x_r = self.reflect(x_c, w)

            x_b = self.simplex[b]
            x_s = self.simplex[s]
            x_w = self.simplex[w]

            fx_b, gx_b = self.eval_fg(self.norm2real(x_b))
            fx_s, gx_s = self.eval_fg(self.norm2real(x_s))
            fx_w, gx_w = self.eval_fg(self.norm2real(x_w))

            optimization_results.n_function_evaluations += 3

            if self.box_feasible(x_r):
                fx_r, gx_r = self.eval_fg(self.norm2real(x_r))
                optimization_results.n_function_evaluations += 1

                if self.is_less_than(fx_r, gx_r, fx_b, gx_b):
                    x_e = self.expand(x_centroid=x_c, x_reflect=x_r)

                    use_reflection = True

                    if self.box_feasible(x_e):
                        fx_e, gx_e = self.eval_fg(self.norm2real(x_e))
                        optimization_results.n_function_evaluations += 1

                        if self.is_less_than(fx_e, gx_e, fx_r, gx_r):
                            self.replace_point(idx=w, x=x_e, fx=fx_e, gx=gx_e)
                            use_reflection = False
                            if debug:
                                print("expansion")

                    if use_reflection:
                        self.replace_point(idx=w, x=x_r, fx=fx_r, gx=gx_r)
                        if debug:
                            print("reflection e")

                elif self.is_less_than(fx_r, gx_r, fx_s, gx_s):
                    self.replace_point(idx=w, x=x_r, fx=fx_r, gx=gx_r)
                    if debug:
                        print("reflection r")

                elif self.is_less_than(fx_r, gx_r, fx_w, gx_w):
                    x_oc = self.outside_contraction(x_centroid=x_c, x_reflect=x_r)

                    use_reflection = True

                    if self.box_feasible(x_oc):
                        fx_oc, gx_oc = self.eval_fg(self.norm2real(x_oc))
                        optimization_results.n_function_evaluations += 1

                        if self.is_less_than(fx_oc, gx_oc, fx_r, gx_r):
                            self.replace_point(idx=w, x=x_oc, fx=fx_oc, gx=gx_oc)
                            use_reflection = False
                            if debug:
                                print("outside contract")

                    if use_reflection:
                        self.replace_point(idx=w, x=x_r, fx=fx_r, gx=gx_r)
                        if debug:
                            print("reflection oc")

                else:
                    x_ic = self.inside_contraction(x_centroid=x_c, x_reflect=x_r)

                    use_shrink = True

                    if self.box_feasible(x_ic):
                        fx_ic, gx_ic = self.eval_fg(self.norm2real(x_ic))
                        optimization_results.n_function_evaluations += 1

                        if self.is_less_than(fx_ic, gx_ic, fx_r, gx_r):
                            self.replace_point(idx=w, x=x_ic, fx=fx_ic, gx=gx_ic)
                            use_shrink = False
                            if debug:
                                print("inside contract")

                    if use_shrink:
                        self.shrink(x_best=x_b)
                        optimization_results.n_function_evaluations += self.dim
                        if debug:
                            print("shrink")

            else:
                x_oc = self.outside_contraction(x_centroid=x_c, x_reflect=x_r)
                x_ic = self.inside_contraction(x_centroid=x_c, x_reflect=x_r)

                fx_ic, gx_ic = self.eval_fg(self.norm2real(x_ic))

                if debug:
                    print("xr infeasible")

                if self.box_feasible(x_oc):

                    x_new = self.min(x_oc, self.min(x_ic, x_w))
                    optimization_results.n_function_evaluations += 4

                    if not all(np.equal(x_new, x_w)):
                        fx_new, gx_new = self.eval_fg(x_new)
                        optimization_results.n_function_evaluations += 1

                        self.replace_point(idx=w, x=x_new, fx=fx_new, gx=gx_new)
                    else:
                        self.shrink(x_best=x_b)
                        optimization_results.n_function_evaluations += self.dim

                elif self.is_less_than(fx_ic, gx_ic, fx_w, gx_w):
                    self.replace_point(idx=w, x=x_ic, fx=fx_ic, gx=gx_ic)

                else:
                    self.shrink(x_best=x_b)
                    optimization_results.n_function_evaluations += self.dim

            index = self.sort_simplex()

            b = index[0]
            s = index[-2]
            w = index[-1]

            x_norms = [np.linalg.norm(x - self.simplex[b], ord=np.inf, axis=0) for x in self.simplex]

            if max(x_norms) < self.eps:
                optimization_results.message = "Stop by norm of the max edge of the simplex less than " + str(self.eps)
                stop = True

            fx_norms = [np.abs(self.f.eval(x) - self.f.eval(self.simplex[b])) for x in self.simplex]

            if max(fx_norms) < self.eps:
                optimization_results.message = "Stop by norm of the max image of the simplex points less than " +\
                                               str(self.eps)
                stop = True

            optimization_results.n_iterations += 1

        optimization_results.x = self.norm2real(self.simplex[b])
        optimization_results.fx = self.fx[b]

        return optimization_results

    def print_simplex(self):
        simplex = np.array(self.simplex)

        print(simplex, '\n')
