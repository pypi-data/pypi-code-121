import multiprocessing
from abc import ABC, abstractmethod

from flex_optimization.core.problem import Problem
from flex_optimization.core.recorder import Recorder


class Method(ABC):
    def __init__(self, problem: Problem, multiprocess: bool | int = False, recorder: Recorder = None):
        self.problem = problem
        self.recorder = self._get_recorder(recorder)
        self.multiprocess = multiprocess

        self.recorder.record(self.recorder.SETUP)

    def __repr__(self):
        return ""

    @abstractmethod
    def run(self):
        ...

    def _get_pool_size(self) -> int:
        if self.multiprocess > 1:
            return self.multiprocess

        return multiprocessing.cpu_count() - 1

    def _get_recorder(self, recorder: Recorder | None) -> Recorder:

        if isinstance(recorder, Recorder):
            if recorder.problem is None:
                recorder.problem = self.problem
            if recorder.method is None:
                recorder.method = self
        else:
            from flex_optimization.recorders.full import RecorderFull
            recorder = RecorderFull(self.problem, self)

        return recorder
