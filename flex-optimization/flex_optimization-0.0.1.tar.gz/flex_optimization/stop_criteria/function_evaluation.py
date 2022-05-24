
from flex_optimization.problem_statement import StopCriteria, Method
from flex_optimization.method_logger import logger


class StopFunctionEvaluation(StopCriteria):
    def __init__(self, num_eval: int = 10):
        self.num_eval = num_eval
        self.current_eval = 0

    def __repr__(self):
        return f"{type(self).__name__} | num_eval: {self.current_eval}"

    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        self.current_eval = method.data.shape[0]
        if self.current_eval >= self.num_eval:
            return False
        logger.debug(f"{type(self).__name__}| current eval: {self.current_eval}/{self.num_eval}")
        return True
