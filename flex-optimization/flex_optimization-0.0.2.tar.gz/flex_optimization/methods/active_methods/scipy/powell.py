import numpy as np

from flex_optimization.core.problem import Problem
from flex_optimization.core.recorder import Recorder
from flex_optimization.core.stop_criteria import StopCriteria
from flex_optimization.methods import MethodType, MethodClassification
from flex_optimization.methods.active_methods.scipy._scipy_base import SciPyBase
from flex_optimization.stop_criteria.function_evaluation import StopFunctionEvaluation


class MethodPowell(SciPyBase):
    """
    Method: Powell algorithm


    steps:
    The method minimises the function by a bi-directional search along each search vector, in turn.


    """

    def __init__(self,
                 problem: Problem,
                 stop_criterion: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 x0: list | tuple | np.ndarray,
                 multiprocess: bool | int = False,
                 recorder: Recorder = None,
                 options: dict = None):
        _method = "Nelder-Mead"
        super().__init__(problem, stop_criterion, x0, multiprocess, recorder, options, _method)

    def method_init(self):
        super().method_init()

        # stopping information
        for stop in self.stop_criterion:
            if stop is isinstance(stop, list):
                continue  # compound stop criteria evaluated in flex_optimization not scip
            elif isinstance(stop, StopFunctionEvaluation):
                if 'options' in self.options:
                    self.options["options"] = self.options["options"] | {"maxfev": stop.num_eval}
                else:
                    self.options["options"] = {"maxfev": stop.num_eval}

        # add defaults


method_class = MethodClassification(
    name="Powell",
    func=MethodPowell,
    type_=MethodType.ACTIVE_LINESEARCH
)
