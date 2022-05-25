# Copyright 2021 Cognite AS
from numbers import Number
from typing import Iterable, List, Union

import numpy as np
import pandas as pd

from .reindex import reindex_many


def is_timeseries(data):
    return isinstance(data, pd.Series) and np.issubdtype(data.index, np.datetime64)


def auto_reindex(data: List[Union[Iterable, Number, pd.Series]], enabled: bool = True):
    """Automatically re-reindex input time series"""

    if not enabled:
        return data

    # Extract sub-list with time-series - only these entries will be reindexed
    id_ts_map = {i: d for i, d in enumerate(data) if is_timeseries(d)}

    # Reindex
    reindexed_ts = reindex_many(list(id_ts_map.values()), bounded=True)

    out = data.copy()
    for idx, ts in zip(id_ts_map.keys(), reindexed_ts):
        out[idx] = ts

    return out


def auto_align(data: List[Union[Iterable, Number, pd.Series]], enabled: bool = True):
    return auto_reindex(data, enabled=enabled)
