
from flex_optimization.problem_statement import StopCriteria, Method


class StopRelativeChange(StopCriteria):
    def __init__(self, cut_off_value: float = 0.01, cut_off_steps: int = 5):
        self.cut_off_value = cut_off_value
        self.cut_off_steps = cut_off_steps
        self.prior_value = None  # min or max
        self.current_cut_off_steps = 0

    def __repr__(self):
        return f"{type(self).__name__} | cut_off_value: {self.cut_off_value}; cut_off_steps: {self.cut_off_steps}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        if self.prior_value is None:  # first iteration
            self.prior_value = method.data.iloc[-1]["metric"]
            return True

        if method.problem.optimization_type:  # max
            return self._evaluate_max(method)

        return self._evaluate_min(method)

    def _evaluate_max(self, method: Method) -> bool:
        result = method.data.iloc[-1]["metric"]
        if result < self.prior_value * (1 + self.cut_off_value):
            self.current_cut_off_steps += 1
            if self.current_cut_off_steps == self.cut_off_steps:
                return False
        else:
            self.current_cut_off_steps = 0  # reset counter with new max bigger than cut off

        if result > self.prior_value:
            self.prior_value = result  # update max

        return True

    def _evaluate_min(self, method: Method) -> bool:
        result = method.data.iloc[-1]["metric"]
        if result > self.prior_value * (1 + self.cut_off_value):
            self.current_cut_off_steps += 1
            if self.current_cut_off_steps == self.cut_off_steps:
                return False
        else:
            self.current_cut_off_steps = 0  # reset counter with new max bigger than cut off

        if result < self.prior_value:
            self.prior_value = result  # update min

        return True
