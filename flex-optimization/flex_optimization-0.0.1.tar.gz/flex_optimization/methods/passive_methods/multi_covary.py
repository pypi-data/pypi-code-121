import itertools
from typing import Union

import numpy as np

from flex_optimization.problem_statement import PassiveMethod, Problem, ContinuousVariable, DiscreteVariable


class MethodMultiCovary(PassiveMethod):
    def __init__(self,
                 levels: Union[int, list[int], tuple[int]],
                 problem: Problem,
                 multiprocess: Union[bool, int] = False):

        self._check_levels(levels)
        self.levels = levels
        super().__init__(problem, multiprocess)

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
            levels = np.linspace(var.min_, var.max_, num_levels).tolist()
            setattr(var, "levels", levels)
        elif isinstance(var, DiscreteVariable):
            setattr(var, "levels", var.items)
        else:
            raise NotImplementedError

    def get_points(self) -> list[list]:
        self._set_levels()
        args = [var.levels for var in self.problem.variables]

        out = []
        for i in range(len(self.problem.variables)):
            args2 = self.flip_arg(args, i)
            out += list(map(list, itertools.zip_longest(*args2, fillvalue=None)))

        return out

    @staticmethod
    def flip_arg(list_: list[list], cut_off: int = 0) -> list[list]:
        out = []
        for i in range(len(list_)):
            sub_list = list_[i]
            if i < cut_off:
                sub_list.reverse()
            out.append(sub_list)

        return out
