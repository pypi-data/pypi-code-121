from typing import Union

from scipy.stats.qmc import MultivariateNormalQMC
from scipy.interpolate import interp1d


from flex_optimization.problem_statement import ActiveMethod, Problem, StopCriteria, \
    ContinuousVariable, DiscreteVariable


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
             stop_criteria: Union[StopCriteria, list[StopCriteria]],
             multiprocess: Union[bool, int] = False, **kwargs):

        self.sobol = MultivariateNormalQMC(mean=[0]*len(problem.variables))
        super().__init__(problem, stop_criteria, multiprocess)

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
