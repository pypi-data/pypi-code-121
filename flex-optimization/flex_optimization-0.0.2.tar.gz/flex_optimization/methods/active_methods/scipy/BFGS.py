import numpy as np

from flex_optimization.core.problem import Problem
from flex_optimization.core.recorder import Recorder
from flex_optimization.core.stop_criteria import StopCriteria
from flex_optimization.methods import MethodType, MethodClassification
from flex_optimization.methods.active_methods.scipy._scipy_base import SciPyBase


class MethodBFGS(SciPyBase):
    """
    Method: Broyden–Fletcher–Goldfarb–Shanno algorithm (BFGS)

    * unconstrained
    * nonlinear

    steps:
    1) determines the descent direction by precondition the gradient with curvature information


    """

    def __init__(self,
                 problem: Problem,
                 stop_criterion: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 x0: list | tuple | np.ndarray,
                 multiprocess: bool | int = False,
                 recorder: Recorder = None,
                 options: dict = None):
        _method = "BFGS"
        super().__init__(problem, stop_criterion, x0, multiprocess, recorder, options, _method)

    def method_init(self):
        super().method_init()

        # remove unsupported feature.
        # TODO: add bounds as a constraint
        del self.options["bounds"]

        # add defaults
        if "jac" not in self.options:
            self.options["jac"] = "2-point"


method_class = MethodClassification(
    name="Broyden–Fletcher–Goldfarb–Shanno (BFGS)",
    func=MethodBFGS,
    type_=MethodType.ACTIVE_GRADIENT
)
