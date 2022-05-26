from typing import Callable

import numpy as np
from scipy.optimize import root, OptimizeResult

from respice.math.optimization.rootsolvers.newton import solve as newton


def solve(eq: Callable,
          x0: np.ndarray,
          args=tuple(),
          jac=None,
          hybr_args=None,
          newton_args=None,
          lm_args=None) -> OptimizeResult:

    if hybr_args is None:
        hybr_args = {}

    try:
        result = root(eq, x0, args=args, method='hybr', jac=jac, **hybr_args)
        if result.success:
            result.step = 'hybr'
            return result
    except OverflowError:
        pass  # The newton solver is more robust against overflows.

    if jac is not None:
        if newton_args is None:
            newton_args = {}

        f = eq if jac is True else lambda x, *args: (eq(x, *args), jac(x, *args))
        result = newton(f, x0, args=args, **newton_args)
        if result.success:
            result.step = 'newton'
            return result

    if lm_args is None:
        lm_args = {}

    result = root(eq, x0, args=args, method='lm', jac=jac, **lm_args)
    result.step = 'lm'
    return result
