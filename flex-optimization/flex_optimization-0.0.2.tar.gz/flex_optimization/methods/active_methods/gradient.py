from typing import Union

import numpy as np
import scipy.optimize

from flex_optimization.problem_statement import ActiveMethod, Problem, StopCriteria, ContinuousVariable, DiscreteVariable

def gradient_descent(gradient, start, learn_rate, n_iter):
    vector = start
    for _ in range(n_iter):
        diff = -learn_rate * gradient(vector)
        vector += diff
    return vector

class MethodRandom(ActiveMethod):

    def __init__(self,
             problem: Problem,
             stop_criteria: Union[StopCriteria, list[StopCriteria], list[list[StopCriteria]]],
             multiprocess: Union[bool, int] = False):

        super().__init__(problem, stop_criteria, multiprocess)

    @staticmethod
    def _select_point(var):
        if isinstance(var, ContinuousVariable):
            return np.random.uniform(var.min_, var.max_, 1)[0]
        elif isinstance(var, DiscreteVariable):
            return random.choice(var.items)
        else:
            raise NotImplementedError

    def get_point(self) -> list:
        return [self._select_point(var) for var in self.problem.variables]

    def get_points(self, num: int) -> list[list]:
        """ Get multiple points. """
        return [[self._select_point(var) for var in self.problem.variables] for _ in range(num)]
