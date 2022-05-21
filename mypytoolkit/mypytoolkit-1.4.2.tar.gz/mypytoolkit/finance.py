# Non-local imports
import numpy as np

def sharpe_ratio(returns: list, risk_free: float):
    """
    Calculates the sharpe ratio of a list of returns.
    Returns must be a list, and risk free rate is required.
    """
    # STD and mean
    returns_std = np.std(returns)
    returns_mean = np.mean(returns)

    return (returns_mean - risk_free) / returns_std