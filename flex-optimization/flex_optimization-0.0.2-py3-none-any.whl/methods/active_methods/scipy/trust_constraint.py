import numpy as np

from flex_optimization.core.problem import Problem
from flex_optimization.core.recorder import Recorder
from flex_optimization.core.stop_criteria import StopCriteria
from flex_optimization.methods import MethodType, MethodClassification
from flex_optimization.methods.active_methods.scipy._scipy_base import SciPyBase


class MethodTrustConstraint(SciPyBase):
    """
    Method: Trust Constraint

    https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html#optimize-minimize-trustconstr

    steps:


    """

    def __init__(self,
                 problem: Problem,
                 stop_criterion: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 x0: list | tuple | np.ndarray,
                 multiprocess: bool | int = False,
                 recorder: Recorder = None,
                 options: dict = None):
        _method = "trust-constr"
        super().__init__(problem, stop_criterion, x0, multiprocess, recorder, options, _method)

    def method_init(self):
        super().method_init()

        del self.options["bounds"]
        # stopping information

        # add defaults
        if "jac" not in self.options:
            self.options["jac"] = "2-point"


method_class = MethodClassification(
    name="Trust Constraint",
    func=MethodTrustConstraint,
    type_=MethodType.ACTIVE_TRUST
)
