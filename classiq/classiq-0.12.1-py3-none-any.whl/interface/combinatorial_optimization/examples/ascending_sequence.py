from typing import List

import numpy as np
import pyomo.core as pyo


def ascending_sequence(coeffs: List[int], bound: int) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    model.x = pyo.Var(
        range(len(coeffs)), domain=pyo.NonNegativeIntegers, bounds=(0, bound)
    )

    @model.Constraint(range(len(coeffs) - 1))
    def monotone_rule(model, idx):
        return model.x[idx] <= model.x[idx + 1]

    model.cost = pyo.Objective(
        expr=coeffs @ np.array(model.x.values()), sense=pyo.maximize
    )

    return model
