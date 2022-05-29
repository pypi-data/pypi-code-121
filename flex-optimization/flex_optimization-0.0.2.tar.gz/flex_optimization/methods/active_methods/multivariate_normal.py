
from scipy.stats.qmc import MultivariateNormalQMC
from scipy.interpolate import interp1d


from flex_optimization.core.recorder import Recorder
from flex_optimization.core.variable import ContinuousVariable, DiscreteVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.method_subclass import ActiveMethod, StopCriteria
from flex_optimization.methods import MethodType, MethodClassification


def map_number(old_value, old_min, old_max, new_min, new_max) -> float:
    if old_value < old_min:
        return new_min
    if old_value > old_max:
        return new_max

    old_span = old_max - old_min
    new_span = new_max - new_min
    scaled_value = float(old_value - old_min) / float(old_span)
    return new_min + (scaled_value * new_span)


class MethodMultiNormal(ActiveMethod):

    def __init__(self,
                 problem: Problem,
                 stop_criteria: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 multiprocess: bool | int = False,
                 recorder: Recorder = None):

        self.sobol = MultivariateNormalQMC(mean=[0]*len(problem.variables))
        super().__init__(problem, stop_criteria, multiprocess, recorder)

    @staticmethod
    def _re_map(var, value):
        if isinstance(var, ContinuousVariable):
            return map_number(value, -3, 3, var.min_, var.max_)
        elif isinstance(var, DiscreteVariable):
            return var.item[int(map_number(value, -3, 3, 0, len(var)-1))]
        else:
            raise NotImplementedError

    def get_point(self) -> list:
        var = self.sobol.random()[0]
        out = []
        for i, v in enumerate(self.problem.variables):
            out.append(self._re_map(v, var[i]))

        return out


method_class = MethodClassification(
    name="multi-normal",
    func=MethodMultiNormal,
    type_=MethodType.ACTIVE_SAMPLING
)
