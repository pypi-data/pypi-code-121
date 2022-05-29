
from flex_optimization.core.method import Method
from flex_optimization.core.stop_criteria import StopCriteria


class StopFunctionEvaluation(StopCriteria):
    """
    Stop Criteria: Function Evaluation

    Stop the algorithm after 'num_eval' function evaluations.

    """
    def __init__(self, num_eval: int = 10):
        self.num_eval = num_eval
        self.current_eval = 0

    def __repr__(self):
        return f"{type(self).__name__} | num_eval: {self.current_eval}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        self.current_eval = len(method.recorder.data)
        if self.current_eval >= self.num_eval:
            return False
        return True
