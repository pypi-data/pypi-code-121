from flex_optimization import OptimizationType
from flex_optimization.core.method import Method
from flex_optimization.core.stop_criteria import StopCriteria


class StopAbsoluteChange(StopCriteria):
    """
    Stop Criteria: Absolute Change

    Stop the algorithm when the best value has not changed more than the 'cut_off_value' for 'cut_off_steps'.
    * setting the 'cut_off_steps' to 1 will cause the algorithm to stop at the first instance when the best value
        doesn't increase by the 'cut_off_value
    * setting the 'cut_off_steps' to >1 will allow the algorithm to continue for 'cut_off_steps' without any
        improvement before stopping. The counter resets each time a new best value bigger than the
        'cut_off_value' is found.

    """
    def __init__(self, cut_off_value: float = 0.01, cut_off_steps: int = 2):
        self.cut_off_value = cut_off_value
        self.cut_off_steps = cut_off_steps
        self.best = None
        self.current_cut_off_steps = 0

    def __repr__(self):
        return f"{type(self).__name__} | cut_off_value: {self.cut_off_value}; cut_off_steps: {self.cut_off_steps}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        # first iteration
        if self.best is None:
            self.best = method.recorder.data[-1][-1]
            return True

        new_point = method.recorder.data[-1][-1]

        # max
        if method.problem.type_ == OptimizationType.MAX:
            return self._evaluate_max(new_point)

        # min
        return self._evaluate_min(new_point)

    def _evaluate_max(self, new_point) -> bool:
        if (new_point - self.best) > self.cut_off_value:
            self.best = new_point  # update max
            self.current_cut_off_steps = 0  # reset counter
            return True  # continue

        self.current_cut_off_steps += 1
        if self.current_cut_off_steps == self.cut_off_steps:
            return False  # stop as too many steps with no improvement

        return True

    def _evaluate_min(self, new_point) -> bool:
        if (self.best - new_point) > self.cut_off_value:
            self.best = new_point  # update min
            self.current_cut_off_steps = 0  # reset counter
            return True  # continue

        self.current_cut_off_steps += 1
        if self.current_cut_off_steps == self.cut_off_steps:
            return False  # stop as too many steps with no improvement

        return True
