import itertools
from typing import List

import pyomo.core as pyo


def set_cover(sub_sets: List[List[int]]) -> pyo.ConcreteModel:
    entire_set = set(itertools.chain(*sub_sets))
    n = max(entire_set)
    num_sets = len(sub_sets)
    assert entire_set == set(
        range(1, n + 1)
    ), f"the union of the subsets is {entire_set} not equal to range(1, {n + 1})"

    model = pyo.ConcreteModel()
    model.x = pyo.Var(range(num_sets), domain=pyo.Binary)

    @model.Constraint(entire_set)
    def independent_rule(model, num):
        return sum(model.x[idx] for idx in range(num_sets) if num in sub_sets[idx]) >= 1

    model.cost = pyo.Objective(expr=sum(model.x.values()), sense=pyo.minimize)

    return model
