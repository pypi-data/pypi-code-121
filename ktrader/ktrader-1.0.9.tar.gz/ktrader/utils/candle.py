import numpy as np
from .date import datetime_to_ts


def get_index_by_date(candle, date, default=0):
    if not date:
        return default
    else:
        ts = datetime_to_ts(date)
        index = np.where(
            candle[:, 0] == ts
        )[0][0]
        return index