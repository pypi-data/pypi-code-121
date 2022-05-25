import numpy as np
import pandas as pd

def numpy_to_dataframe(data, timestamps=None, data_column_names=None, time_column_name=None, copy=False):
    assert(isinstance(data, np.ndarray))
    if len(data.shape)==1:
        data = np.expand_dims(data, axis=-1)
    [N, dim] = data.shape
    if data_column_names is None:
        data_column_names = ['d_%d'%i for i in range(dim)]
    assert(isinstance(data_column_names, list))
    assert(len(data_column_names)==dim)
    if timestamps is not None:
        assert(len(timestamps)==N)
        timestamps = np.asarray(timestamps)
        timestamps = timestamps if len(timestamps.shape)==2 else np.expand_dims(timestamps, axis=-1)
        data = np.hstack([timestamps, data])
        tname = time_column_name if time_column_name is not None else 'timestamp'
        data_column_names = [tname] + data_column_names
    return pd.DataFrame(data=data, columns=data_column_names, copy=copy)


def timeseries_to_numpy(data):
    """
    Convert autoai_ts_libs.deps.tspy.TimeSeries to two numpy objects: data and timestamps
    Args:
        data: TimeSeries() object

    Returns: numpy (data), numpy (timeseries)

    """
    xnp = data.to_df(convert_dates=False).to_numpy()
    return xnp[:, 1:], xnp[:, 0]


