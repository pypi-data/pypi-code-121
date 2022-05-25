import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from multiprocessing import cpu_count


def applyParallel(dfGrouped, func):
    retLst = Parallel(n_jobs=cpu_count() - 4, verbose=10)(
        delayed(func)(group) for name, group in dfGrouped)
    return pd.concat(retLst)


def applyParallel_lstm(
    dfGrouped, func, n_neurons, week_in, week_out, forecast_horizon, epochs,
        use_dropout, error_factor):
    retLst = Parallel(n_jobs=cpu_count() - 4, verbose=10)(delayed(func)(
        group, n_neurons=n_neurons, week_in=week_in, week_out=week_out,
        forecast_horizon=forecast_horizon, epochs=epochs,
        use_dropout=use_dropout, error_factor=error_factor)
        for name, group in dfGrouped)
    return pd.concat(retLst)


def sum_std(x):
    x = np.square(x)
    x = np.sqrt(sum(x))
    return round(x)


def list_to_sql(normal_list):
    """
    Converts normal list to string for sql query uses
    Parameters:
        normal_list: (list) list of values [1, 2, 'a', 'b']
    Returns:
        sql_list: (str) of values (1, 2, 'a', 'b')
    """
    return str(normal_list).replace('[', '(').replace(']', ')')