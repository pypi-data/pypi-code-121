
from scipy.stats.qmc import Halton
from scipy.interpolate import interp1d

from flex_optimization.core.recorder import Recorder
from flex_optimization.core.variable import ContinuousVariable, DiscreteVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.method_subclass import ActiveMethod, StopCriteria
from flex_optimization.methods import MethodType, MethodClassification


def map_number(old_value, old_min, old_max, new_min, new_max) -> float:
    return float(interp1d([old_min, old_max], [new_min, new_max])(old_value))


class MethodHalton(ActiveMethod):

    def __init__(self,
                 problem: Problem,
                 stop_criteria: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 multiprocess: bool | int = False,
                 recorder: Recorder = None):

        self.halton = Halton(d=len(problem.variables))
        super().__init__(problem, stop_criteria, multiprocess, recorder)

    def get_point(self) -> list:
        var = self.halton.random()[0]
        out = []
        for i, v in enumerate(self.problem.variables):
            if isinstance(v, ContinuousVariable):
                out.append(map_number(var[i], 0, 1, v.min_, v.max_))
            elif isinstance(v, DiscreteVariable):
                out.append(v.item[int(map_number(var[i], 0, 1, 0, len(v)-1))])
            else:
                raise NotImplementedError

        return out


method_class = MethodClassification(
    name="Halton",
    func=MethodHalton,
    type_=MethodType.ACTIVE_SAMPLING
)
