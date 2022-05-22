from typing import List, Optional

import numpy as np
import pyomo.core as pyo


def knapsack(
    values: List[int],
    upper_bound: int,
    weights: Optional[List[int]] = None,
    max_weight: Optional[int] = None,
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()

    model.x = pyo.Var(
        range(len(values)), domain=pyo.NonNegativeIntegers, bounds=(0, upper_bound)
    )

    if max_weight is not None and weights is not None:
        assert len(values) == len(
            weights
        ), "values and weights must be with the same length"
        model.weight_constraint = pyo.Constraint(
            expr=weights @ np.array(model.x.values()) <= max_weight
        )

    model.cost = pyo.Objective(
        expr=values @ np.array(model.x.values()), sense=pyo.maximize
    )

    return model
