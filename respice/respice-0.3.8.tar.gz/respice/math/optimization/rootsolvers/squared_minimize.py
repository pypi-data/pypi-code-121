import numpy as np
from scipy.optimize import minimize


def solve(fun, x0, jac=None, args=tuple(), method='Nelder-Mead'):
    def f(x, *args):
        fx = fun(x, *args)

        if jac is None:
            return np.sum(np.square(fx))

        if jac is True:
            fx, j = fx
        else:
            j = jac(fx, *args)

        resid = np.sum(np.square(fx))
        resid_grad = 2 * (np.transpose(j) @ fx)

        return resid, resid_grad

    return minimize(f, x0, args=args, jac=None if jac is None else True, method=method)
