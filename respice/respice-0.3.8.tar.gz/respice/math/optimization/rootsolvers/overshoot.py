"""
Implementation of the "overshoot" type solver, an enhanced wrapper around SciPy's `root`.

It is a naive and simple solver which attempts to overshoot solutions on stationary locations and retries solving.
"""
import math
import warnings
from typing import Callable

import numpy as np
from scipy.optimize import root, OptimizeResult


# This solver is deprecated! It exists solely for legacy and compatibility purposes!


class UnmetPrecisionWarning(UserWarning):
    def __init__(self, msg: str, result: OptimizeResult):
        super().__init__(msg)

        self.result = result


def _disturb_solution(trial: int, solution: OptimizeResult, factor_multiplier=100) -> np.ndarray:
    """
    Disturbs the result of a solution. This function is used when retrying the solution because convergence
    didn't succeed and has gotten so worse that the solver stops further trying. Trying with a different starting
    point is the recommended method.

    This function specifically applies relative disturbance and considers the direction of the Jacobian matrix
    to effectively over-shoot the current (non-converged) solution. The higher the trial number, the higher
    the overshooting.

    :param trial:
        The current trial number (starts from 1).
    :param solution:
        The `OptimizationResult` as received from `scipy.optimize.root`.
    :param factor_multiplier:
        The disturbance factor to the trial.
    :return:
        The disturbed solution vector.
    """
    directional_multiplier = np.array([(-1 if v < 0 else 1) for v in solution.fjac @ solution.x])
    return directional_multiplier * factor_multiplier ** trial * solution.x


def solve(eq: Callable, x0: np.ndarray, args=tuple(), jac=None, method='hybr') -> OptimizeResult:
    """
    Attempts to solve the given electrical-circuit-governing system equation.

    Additionally employs retries if convergence tolerances are not reached with different starting points
    utilizing `_disturb_solution`. If `_disturb_solution` does yield conversion to the same (or rather very close
    point), then again a retry is attempted, but with a point that's more far away. If other points are hit that
    still don't fulfill convergence restrictions, retries are attempted on them as well. Retries are tracked per
    solution, so in case that we encounter cycles where we jump to different but non-satisfying solutions and come
    back to a solution we already had, `_disturb_solution` will attempt a different start vector never used before
    to not end up in useless wastes of trials.

    By default int((math.log10(len(start_vector)) + 1) * 4) trials will be attempted if needed, so for larger
    systems more points are investigated for bad convergence. To not increase evaluation time too much, the
    logarithm is used to only scale to the order of the system.

    :param eq:
        The system equation function to solve.
    :param x0:
        The initial start vector.
    :param args:
        Args to `eq` and `jac`.
    :param jac:
        The Jacobian (function) of eq.
    :param method:
        Which root solver method to use.
        See https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html.
    :return:
        The solution (or on non-convergence, the closest solution found during the process).
    """
    unsatisfying_results = []
    trials = {}
    retries = int((math.log10(len(x0)) + 1) * 4)
    for trial in range(retries):
        result = root(
            eq,
            x0,
            args=args,
            method=method,
            jac=jac,
        )

        if result.success:
            break

        unsatisfying_results.append(result)

        # Result disturbance is a bit smarter and resets the trial count if we really found a different point,
        # so in case the next different value again does not converge, we do not overshoot extremely just because
        # this happened at a high trial count. However, if we might re-encounter the same solution, then the old
        # trial count gets restored again. That ensures that we really always try out new values and aren't driven
        # into useless re-evaluation of the same points until all trials are exhausted.
        for solution in trials:
            if math.isclose(np.linalg.norm(solution), np.linalg.norm(result.x)):
                trials[solution] += 1
                result_trials = trials[solution]
                break
        else:
            trials[tuple(result.x)] = 1  # numpy arrays are not hashable, so we produce a hashable vector.
            result_trials = 1

        x0 = _disturb_solution(result_trials, result)
    else:
        # Filter out best result closest to zero.
        result = min(unsatisfying_results, key=lambda x: np.linalg.norm(x.fun))

        warnings.warn(UnmetPrecisionWarning(
            'Failed to converge after several retries. Taking the closest result as granted.',
            result,
        ))

    return result
