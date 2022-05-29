from flex_optimization import OptimizationType
from flex_optimization.core.method import Method
from flex_optimization.core.stop_criteria import StopCriteria

# TODO: update this and add to options
class StopRelativeRate(StopCriteria):
    def __init__(self, cut_off_rate: float = 0.01, prior_steps: int = 3, cut_off_steps: int = 3):
        raise NotImplementedError("coming soon")
        self.cut_off_rate = cut_off_rate
        self.prior_steps = prior_steps
        self.cut_off_steps = cut_off_steps
        self.prior_values = None  # min or max
        self.current_cut_off_steps = 0

    def __repr__(self):
        return f"{type(self).__name__} | cut_off_value: {self.cut_off_value}; cut_off_steps: {self.cut_off_steps}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        if len(method.data) < self.prior_steps:  # first iterations
            return True

        if method.problem.type_ == OptimizationType.MAX:  # max
            return self._evaluate_max(method)

        return self._evaluate_min(method)

    def _evaluate_max(self, method: Method) -> bool:
        result = method.data.iloc[self.prior_steps:-1]["metric"]
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
