import math
import typing

import numpy as np
import pandas as pd

if typing.TYPE_CHECKING:
    from kolibri.task.timeseries import TimeSeriesData


def get_anomalies_median(ts, window_size: int = 10, alpha: float = 3):
    """
    Get point outliers in time series using median model (estimation model-based method).
    Outliers are all points deviating from the median by more than alpha * std, where std is the sample variance in the window.

    Parameters
    ----------
    ts:
        TSDataset with timeseries data
    in_column:
        name of the column in which the anomaly is searching
    window_size:
        number of points in the window
    alpha:
        coefficient for determining the threshold

    Returns
    -------
    :
        dict of outliers in format {segment: [outliers_timestamps]}
    """
    outliers_per_segment_group = {}
    segments = ts.segments
    groups=ts.groups

    for seg in segments:
        outliers_per_group={}
        for grp in groups:
            anomalies = []
            segment_df = ts.df[ts.df.index.get_level_values(0)==grp][seg].reset_index()

            values = segment_df[ts.target].values
            timestamp = segment_df[ts.timestamp].values

            n_iter = math.ceil(len(values) / window_size)
            for i in range(n_iter):
                left_border = i * window_size
                right_border = min(left_border + window_size, len(values))
                med = np.median(values[left_border:right_border])
                std = np.std(values[left_border:right_border])
                diff = np.abs(values[left_border:right_border] - med)
                anomalies.extend(np.where(diff > std * alpha)[0] + left_border)
            outliers_per_group[grp]= [timestamp[i] for i in anomalies]
        outliers_per_segment_group[seg] = outliers_per_group
    return outliers_per_segment_group
