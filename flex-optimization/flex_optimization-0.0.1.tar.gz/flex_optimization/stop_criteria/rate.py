import numpy as np
from scipy import stats

from flex_optimization.problem_statement import StopCriteria, Method


def _linear_regression(x: np.ndarray, y: np.ndarray):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope


class StopRate(StopCriteria):
    def __init__(self, cut_off_rate: float = 0.01, prior_steps: int = 3, cut_off_steps: int = 3):
        self.cut_off_rate = cut_off_rate
        self.prior_steps = prior_steps
        self.cut_off_steps = cut_off_steps
        self.current_cut_off_steps = 0

    def __repr__(self):
        return f"{type(self).__name__} | cut_off_rate: {self.cut_off_rate}; prior_steps: {self.prior_steps}; " \
               f"cut_off_steps: {self.cut_off_steps}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        if len(method.data) < self.prior_steps:  # first iterations
            return True

        if method.problem.optimization_type:  # max
            return self._evaluate_max(method)

        return self._evaluate_min(method)

    def _evaluate_max(self, method: Method) -> bool:
        results = method.data.iloc[-self.prior_steps:]["metric"]
        slope = _linear_regression(np.linspace(0, self.prior_steps-1, self.prior_steps), results.to_numpy())

        if slope < self.cut_off_rate:
            self.current_cut_off_steps += 1
            if self.current_cut_off_steps == self.cut_off_steps:
                return False
        else:
            self.current_cut_off_steps = 0  # reset counter with new steep slope

        return True

    def _evaluate_min(self, method: Method) -> bool:
        results = method.data.iloc[self.prior_steps:-1]["metric"]
        slope = _linear_regression(np.linspace(0, self.prior_steps-1, self.prior_steps), results.to_numpy())

        if slope > self.cut_off_rate:
            self.current_cut_off_steps += 1
            if self.current_cut_off_steps == self.cut_off_steps:
                return False
        else:
            self.current_cut_off_steps = 0  # reset counter with new steep slope

        return True
