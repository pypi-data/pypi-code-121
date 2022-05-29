
from flex_optimization.core.method import Method


class StopCriteria:
    def evaluate(self, method: Method, *args, **kwargs) -> bool:
        """ True = Continue; False = Stop """
        pass
