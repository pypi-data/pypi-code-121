from flex_optimization import OptimizationType


class ProblemClassification:
    population = []

    def __init__(self, name: str, func: callable, type_: OptimizationType, global_goal: callable, range_: tuple,
                 local_min: int, num_dim: tuple, convex: True, roughness: int, symmetric: bool):
        self.name = name
        self.func = func
        self.type_ = type_
        self.global_goal = global_goal
        self.range_ = range_
        self.local_min = local_min
        self.num_dim = num_dim
        self.convex = convex
        self.roughness = roughness  # [0, 10] 0 = smooth, 10 = rough
        self.symmetric = symmetric

        ProblemClassification.population.append(self)

    def __repr__(self):
        return f"{self.name} | {self.num_dim}"


from flex_optimization.problems.gaussian import nd_gaussian
from flex_optimization.problems.ackley import ackley
from flex_optimization.problems.rastrigin import rastrigin
from flex_optimization.problems.sphere import sphere
from flex_optimization.problems.rosenbrock import rosenbrock
from flex_optimization.problems.rosenbrock_variant import rosenbrock_variant

# TODO: for more functions https://en.wikipedia.org/wiki/Test_functions_for_optimization
