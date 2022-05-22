from typing import List, Tuple

import numpy as np
import pyomo.core as pyo


def portfolio_optimization_binary(
    covariances: np.ndarray, returns: np.ndarray, budget: int
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    num_assets = len(returns)
    model.x = pyo.Var(range(num_assets), domain=pyo.Binary)
    x_array = model.x.values()

    model.budget = pyo.Constraint(expr=(sum(x_array) == budget))

    risk: float = x_array @ covariances @ x_array
    profit: float = returns @ x_array
    model.risk, model.profit = risk, profit

    model.cost = pyo.Objective(expr=model.risk - model.profit, sense=pyo.minimize)

    return model


def portfolio_optimization_binary_ineq(
    covariances: np.ndarray, returns: np.ndarray, budget: int
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    num_assets = len(returns)
    model.x = pyo.Var(range(num_assets), domain=pyo.Binary)
    x_array = model.x.values()

    model.budget = pyo.Constraint(expr=(sum(x_array) <= budget))

    risk: float = x_array @ covariances @ x_array
    profit: float = returns @ x_array
    model.risk, model.profit = risk, profit

    model.cost = pyo.Objective(expr=model.risk - model.profit, sense=pyo.minimize)

    return model


def portfolio_optimization_integer_no_constraint(
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


def portfolio_optimization_integer_ineq(
    covariances: np.ndarray, returns: np.ndarray, budget: int, upper_bounds: List[int]
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    num_assets = len(returns)

    def bounds(_, i):
        return 0, upper_bounds[i]

    model.x = pyo.Var(range(num_assets), domain=pyo.NonNegativeIntegers, bounds=bounds)

    x_array: np.ndarray = np.array(model.x.values())
    model.budget = pyo.Constraint(expr=(sum(x_array) <= budget))
    risk: float = x_array @ covariances @ x_array
    profit: float = returns @ x_array
    model.risk, model.profit = risk, profit

    model.cost = pyo.Objective(expr=model.risk - model.profit, sense=pyo.minimize)

    return model


def portfolio_optimization_negative_integer_ineq(
    covariances: np.ndarray,
    returns: np.ndarray,
    budget: int,
    bounds: List[Tuple[int, int]],
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    num_assets = len(returns)

    model.x = pyo.Var(
        range(num_assets), domain=pyo.Integers, bounds=lambda _, idx: bounds[idx]
    )

    x_array: np.ndarray = np.array(model.x.values())
    model.budget = pyo.Constraint(expr=(sum(x_array) <= budget))
    risk: float = x_array @ covariances @ x_array
    profit: float = returns @ x_array
    model.risk, model.profit = risk, profit

    model.cost = pyo.Objective(expr=model.risk - model.profit, sense=pyo.minimize)

    return model
