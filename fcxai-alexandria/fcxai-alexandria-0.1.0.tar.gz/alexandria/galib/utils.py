import pandas as pd


def get_dates(start_date, end_date):
    dates = pd.date_range(start_date, end_date, freq="1D")
    dates = pairwise(dates)
    dates = [(a, (b - pd.DateOffset(1))) for a, b in dates[:-1]] + [dates[-1]]
    dates = [(a.strftime("%F"), b.strftime("%F")) for (a, b) in dates]
    return dates


def pairwise(s):
    """
    [1, 2, 3, 4, 5, 6] => [(1,2), (2,3), (3,4), ...]
    """
    return list(zip(s[:-1], s[1:]))
