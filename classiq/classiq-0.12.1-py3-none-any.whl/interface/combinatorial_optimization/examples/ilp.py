import numpy as np
import pyomo.core as pyo


def ilp(a: np.ndarray, b: np.ndarray, c: np.ndarray, bound: int) -> pyo.ConcreteModel:
    # model constraint: a*x <= b
    model = pyo.ConcreteModel()
    assert b.ndim == c.ndim == 1

    num_vars = len(c)
    num_constraints = len(b)

    assert a.shape == (num_vars, num_constraints)

    model.x = pyo.Var(
        range(num_vars), domain=pyo.NonNegativeIntegers, bounds=(0, bound)
    )

    @model.Constraint(range(num_constraints))
    def monotone_rule(model, idx):
        return a[idx, :] @ model.x.values() <= b[idx]

    # model objective: max(c * x)
    model.cost = pyo.Objective(expr=c @ model.x.values(), sense=pyo.maximize)

    return model
