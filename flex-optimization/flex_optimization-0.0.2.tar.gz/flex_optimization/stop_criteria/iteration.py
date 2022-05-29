
from flex_optimization.core.method_subclass import ActiveMethod
from flex_optimization.core.stop_criteria import StopCriteria


class StopIterationEvaluation(StopCriteria):
    """
    Stop Criteria: Function Iteration

    Stop the algorithm after 'num_eval' iterations.
    * an iteration may be 1 function evaluation; but it may not be.

    """
    def __init__(self, num_eval: int = 10):
        self.num_eval = num_eval
        self.current_eval = 0

    def __repr__(self):
        return f"{type(self).__name__} | num_eval: {self.current_eval}"

    def evaluate(self, method: ActiveMethod, *args, **kwargs) -> bool:
        if method.iteration_count >= self.num_eval:
            return False
        return True
