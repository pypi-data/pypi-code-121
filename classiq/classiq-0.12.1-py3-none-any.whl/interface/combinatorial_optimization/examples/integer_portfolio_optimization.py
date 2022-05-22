from typing import List

import numpy as np
import pyomo.core as pyo


def integer_portfolio_optimization(
    covariances: np.ndarray, returns: np.ndarray, upper_bounds: List[int]
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    num_assets = len(returns)

    def bounds(_, i):
        return 0, upper_bounds[i]

    model.x = pyo.Var(range(num_assets), domain=pyo.NonNegativeIntegers, bounds=bounds)

    x_array: np.ndarray = np.array(model.x.values())
    risk: float = x_array @ covariances @ x_array
    profit: float = returns @ x_array
    model.risk, model.profit = risk, profit

    model.cost = pyo.Objective(expr=model.risk - model.profit, sense=pyo.minimize)

    return model
