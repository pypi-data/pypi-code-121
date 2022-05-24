from typing import Union

import numpy as np
from scipy.optimize import minimize

from flex_optimization.problem_statement import ActiveMethod, Problem, StopCriteria, ContinuousVariable, \
    DiscreteVariable
from flex_optimization.utils.scalar_function import ScalarFunction
from flex_optimization.utils.linesearch import _line_search_wolfe12, _LineSearchError


# def vecnorm(x, ord=2):
#     if ord == np.Inf:
#         return np.amax(np.abs(x))
#     elif ord == -np.Inf:
#         return np.amin(np.abs(x))
#     else:
#         return np.sum(np.abs(x) ** ord, axis=0) ** (1.0 / ord)
#
#
# def _minimize_bfgs(fun, x0, args=(), jac=None, callback=None,
#                    gtol=1e-5, norm=np.Inf, eps=None, maxiter=None,
#                    return_all=False, finite_diff_rel_step=None,
#                    **unknown_options):
#     """
#     Minimization of scalar function of one or more variables using the
#     BFGS algorithm.
#     Options
#     -------
#     maxiter : int
#         Maximum number of iterations to perform.
#     gtol : float
#         Gradient norm must be less than `gtol` before successful
#         termination.
#     norm : float
#         Order of norm (Inf is max, -Inf is min).
#     eps : float or ndarray
#         If `jac is None` the absolute step size used for numerical
#         approximation of the jacobian via forward differences.
#     return_all : bool, optional
#         Set to True to return a list of the best solution at each of the
#         iterations.
#     finite_diff_rel_step : None or array_like, optional
#         If `jac in ['2-point', '3-point', 'cs']` the relative step size to
#         use for numerical approximation of the jacobian. The absolute step
#         size is computed as ``h = rel_step * sign(x0) * max(1, abs(x0))``,
#         possibly adjusted to fit into the bounds. For ``method='3-point'``
#         the sign of `h` is ignored. If None (default) then step is selected
#         automatically.
#     """
#
# def init():
#     x0 = np.asarray(x0).flatten()
#     if x0.ndim == 0:
#         x0.shape = (1,)
#     if maxiter is None:
#         maxiter = len(x0) * 200
#
#     sf = ScalarFunction(fun, x0, jac, epsilon=eps, finite_diff_rel_step=finite_diff_rel_step)
#
#     f = sf.fun
#     myfprime = sf.grad
#
#     old_fval = f(x0)
#     gfk = myfprime(x0)
#
#     k = 0
#     N = len(x0)
#     I = np.eye(N, dtype=int)
#     Hk = I
#
#     # Sets the initial step guess to dx ~ 1
#     old_old_fval = old_fval + np.linalg.norm(gfk) / 2
#
#     xk = x0
#     warnflag = 0
#     gnorm = vecnorm(gfk, ord=norm)
#     while (gnorm > gtol) and (k < maxiter):
#
# def main_loop():
#     pk = -np.dot(Hk, gfk)
#     try:
#         alpha_k, fc, gc, old_fval, old_old_fval, gfkp1 = \
#             _line_search_wolfe12(f, myfprime, xk, pk, gfk, old_fval, old_old_fval, amin=1e-100, amax=1e100)
#
#     except _LineSearchError:
#         # Line search failed to find a better solution.
#         warnflag = 2
#         break
#
#     xkp1 = xk + alpha_k * pk
#     sk = xkp1 - xk
#     xk = xkp1
#     if gfkp1 is None:
#         gfkp1 = myfprime(xkp1)
#
#     yk = gfkp1 - gfk
#     gfk = gfkp1
#     if callback is not None:
#         callback(xk)
#     k += 1
#     gnorm = vecnorm(gfk, ord=norm)
#     if (gnorm <= gtol):
#         break
#
#     if not np.isfinite(old_fval):
#         # We correctly found +-Inf as optimal value, or something went
#         # wrong.
#         warnflag = 2
#         break
#
#     rhok_inv = np.dot(yk, sk)
#     # this was handled in numeric, let it remains for more safety
#     if rhok_inv == 0.:
#         rhok = 1000.0
#     else:
#         rhok = 1. / rhok_inv
#
#     A1 = I - sk[:, np.newaxis] * yk[np.newaxis, :] * rhok
#     A2 = I - yk[:, np.newaxis] * sk[np.newaxis, :] * rhok
#     Hk = np.dot(A1, np.dot(Hk, A2)) + (rhok * sk[:, np.newaxis] * sk[np.newaxis, :])
#
#
#     return


class MethodBFGS(ActiveMethod):

    def __init__(self,
                 problem: Problem,
                 stop_criteria: Union[StopCriteria, list[StopCriteria], list[list[StopCriteria]]],
                 x0,
                 multiprocess: Union[bool, int] = False,
                 ):

        self.x0 = x0

        super().__init__(problem, stop_criteria, multiprocess)

    def run(self, guard_value: int = 1_000):
        if self.problem.optimization_type:
            def maximize_func(*args, **kwargs):
                return -1 * self.problem.evaluate(*args, **kwargs)
            func = maximize_func
        else:
            func = self.problem.evaluate

        r = minimize(func, self.x0, method='BFGS', jac='2-point', callback=self.callback)
        print(r)

    def callback(self, *args, **kwargs):
        print(args)

    def get_point(self) -> list:
        pass


    def main_loop(self):
        pass