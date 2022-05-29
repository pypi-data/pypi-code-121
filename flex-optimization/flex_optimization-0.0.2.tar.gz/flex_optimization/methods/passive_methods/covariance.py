
import numpy as np

from flex_optimization.core.recorder import Recorder
from flex_optimization.core.variable import ContinuousVariable, DiscreteVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.method_subclass import PassiveMethod
from flex_optimization.methods import MethodClassification, MethodType


class MethodCovariance(PassiveMethod):
    """
    Method: Covariance

    Method picks points by varying one or more factors linearly across the domain.


    """
    def __init__(self,
                 problem: Problem,
                 levels: int | list[int] | tuple[int],
                 multiprocess: bool | int = False,
                 recorder: Recorder = None):

        self._check_levels(levels)
        self.levels = levels
        super().__init__(problem, multiprocess, recorder)

    @staticmethod
    def _check_levels(levels):
        if isinstance(levels, int):
            if levels < 1:
                raise ValueError("levels must be greater than 1")
        elif isinstance(levels, (tuple, list)):
            for level in levels:
                if isinstance(level, int):
                    if level < 1:
                        raise ValueError("levels must be greater than 1")
        else:
            raise TypeError

    def _set_levels(self):
        if isinstance(self.levels, int):
            for var in self.problem.variables:
                self._set_level(var, self.levels)
            return

        for var, num_levels in zip(self.problem.variables, self.levels):
            self._set_level(var, num_levels)

    @staticmethod
    def _set_level(var, num_levels: int):
        if isinstance(var, ContinuousVariable):
            levels = np.linspace(var.min_, var.max_, num_levels)
            setattr(var, "levels", levels)
        elif isinstance(var, DiscreteVariable):
            setattr(var, "levels", var.items)
        else:
            raise NotImplementedError

    def get_points(self) -> list[list]:
        self._set_levels()
        args = [var.levels for var in self.problem.variables]

        import itertools
        return list(map(list, itertools.zip_longest(*args, fillvalue=None)))


method_class = MethodClassification(
    name="covariance",
    func=MethodCovariance,
    type_=MethodType.PASSIVE_SAMPLING
)
