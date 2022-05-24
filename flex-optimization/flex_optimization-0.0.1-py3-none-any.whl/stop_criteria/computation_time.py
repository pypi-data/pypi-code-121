import time

from flex_optimization.problem_statement import StopCriteria


class StopComputationTime(StopCriteria):
    def __init__(self, duration: float = 120):
        self.duration = duration  # seconds
        self.start_time = time.monotonic()  # seconds
        self.stop_time = time.monotonic() + duration

    def __repr__(self):
        return f"{type(self).__name__} | duration: {self.duration}"

    def evaluate(self, *args, **kwargs) -> bool:
        if self.stop_time < time.monotonic():
            return False

        return True
