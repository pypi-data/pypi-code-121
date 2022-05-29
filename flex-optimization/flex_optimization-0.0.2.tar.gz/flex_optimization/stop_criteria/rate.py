import numpy as np
from scipy import stats

from flex_optimization import OptimizationType
from flex_optimization.core.method import Method
from flex_optimization.core.stop_criteria import StopCriteria


def _linear_regression(x: np.ndarray, y: np.ndarray):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope


class StopRate(StopCriteria):
    """
    Stop Criteria: Rate

    Stop the algorithm after 'cut_off_steps' iterations of the slope of the past 'prior_steps' falls below the
    'cut_off_rate'.

    """
    def __init__(self, cut_off_rate: float = 0.01, prior_steps: int = 3, cut_off_steps: int = 3):
        self.cut_off_rate = cut_off_rate
        self.prior_steps = prior_steps
        self.cut_off_steps = cut_off_steps
        self.current_cut_off_steps = 0
        self.data = []
        self._x = np.linspace(0, self.prior_steps-1, self.prior_steps)

    def __repr__(self):
        return f"{type(self).__name__} | cut_off_rate: {self.cut_off_rate}; prior_steps: {self.prior_steps}; " \
               f"cut_off_steps: {self.cut_off_steps}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        # first iterations
        if len(self.data) < self.prior_steps:
            self.data.append(method.recorder.data[-1][-1])
            return True

        self.data.pop(0)
        self.data.append(method.recorder.data[-1][-1])
        slope = _linear_regression(self._x, np.array(self.data))

        # max
        if method.problem.type_ == OptimizationType.MAX:
            return self._evaluate_max(slope)

        # min
        return self._evaluate_min(slope)

    def _evaluate_max(self, slope: float) -> bool:
        if slope < self.cut_off_rate:
            self.current_cut_off_steps += 1
            if self.current_cut_off_steps == self.cut_off_steps:
                return False
        else:
            self.current_cut_off_steps = 0  # reset counter with new steep slope

        return True

    def _evaluate_min(self, slope: float) -> bool:
        if slope > self.cut_off_rate:
            self.current_cut_off_steps += 1
            if self.current_cut_off_steps == self.cut_off_steps:
                return False
        else:
            self.current_cut_off_steps = 0  # reset counter with new steep slope

        return True
