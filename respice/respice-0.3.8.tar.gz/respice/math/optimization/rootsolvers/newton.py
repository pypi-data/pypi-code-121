from typing import Callable, Optional

import numpy as np
from scipy.optimize import OptimizeResult


def solve(f: Callable,
          x0: np.ndarray,
          tol: float = 1.49012e-08,
          args=tuple(),
          stepbound: float = None,
          maxiter: Optional[int] = None,
          overflow_stepfactor: float = 0.5) -> OptimizeResult:

    if maxiter is None:
        maxiter = 200 * len(x0)

    x = x0.astype('float64')

    delta = 0
    delta_norm = 0

    for _ in range(maxiter):
        while True:
            try:
                F, J = f(x, *args)
            except OverflowError:
                if delta_norm < tol:
                    raise
                delta_norm *= overflow_stepfactor
                delta *= overflow_stepfactor
                x -= delta
            else:
                break

        delta = np.linalg.solve(J, -F)

        if any(np.isnan(d) for d in delta):
            return OptimizeResult({
                'x': x,
                'success': False,
                'fun': F,
                'fjac': J,
                'message': f'Encountered invalid float.',
            })

        delta_norm = np.linalg.norm(delta)

        if stepbound is not None:
            if delta_norm > stepbound:
                delta *= stepbound / delta_norm

        x += delta
        if delta_norm < tol:
            break
    else:
        F, J = f(x, *args)
        return OptimizeResult({
            'x': x,
            'success': False,
            'fun': F,
            'fjac': J,
            'message': f'Exceeded number of iterations ({maxiter}).',
        })

    F, J = f(x, *args)
    return OptimizeResult({
        'x': x,
        'success': True,
        'fun': F,
        'fjac': J,
        'message': 'The algorithm converged.',
    })
