"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
"""
#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

import pandas as pd

from autoai_ts_libs.deps.tspy.data_structures import TRS
from autoai_ts_libs.deps.tspy.data_structures.io.TimeSeriesReader import TimeSeriesReader
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries
from autoai_ts_libs.deps.tspy import _get_context
import datetime
import logging

from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries

log = logging.getLogger(__name__)

def _observations(tsc, observations, granularity=None, start_time=None):
    """
    create a time-series from a collection of observations

    Parameters
    ----------
    observations : :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        collection of observations
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    stwwart_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries
        a new time-series

    Examples
    --------
    create a collection of observations

    >>> import autoai_ts_libs.deps.tspy
    >>> observations = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(0,0)).add(autoai_ts_libs.deps.tspy.observation(1,1)).result()
    >>> observations
    [(0,0),(1,1)]

    create a time-series from observations

    >>> ts = autoai_ts_libs.deps.tspy.time_series(observations)
    >>> ts
    TimeStamp: 0     Value: 0
    TimeStamp: 1     Value: 1

    create a time-series from observations with a time-reference system

    >>> import datetime
    >>> granularity = datetime.timedelta(days=1)
    >>> start_time = datetime.datetime(1990,7,6)
    >>> ts = autoai_ts_libs.deps.tspy.time_series(observations, granularity, start_time)
    >>> ts
    TimeStamp: 1990-07-06T00:00Z     Value: 0
    TimeStamp: 1990-07-07T00:00Z     Value: 1
    """
    if granularity is None and start_time is None:
        return TimeSeries(
            tsc,
            tsc.packages.time_series.core.timeseries.TimeSeries.fromObservations(
                observations._j_observations)
        )
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        trs = TRS(tsc, granularity, start_time)
        return TimeSeries(
            tsc,
            tsc.packages.time_series.core.timeseries.TimeSeries.fromObservations(
                observations._j_observations,
                trs._j_trs
            ),
            trs
        )


def _list(tsc, list_of_values, granularity=None, start_time=None):
    """
    create a time-series from a list of values

    Parameters
    ----------
    list_of_values : list
        list of values
    ts_func : func
        function to combine duplicate time-ticks (default is do not combine)
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries
        a new time-series

    Examples
    --------
    create a time-series from a list of values

    >>> ts = autoai_ts_libs.deps.tspy.time_series([0, 1])
    >>> ts
    TimeStamp: 0     Value: 0
    TimeStamp: 1     Value: 1

    create a time-series from a list of values with a time-reference system

    >>> import datetime
    >>> granularity = datetime.timedelta(days=1)
    >>> start_time = datetime.datetime(1990,7,6)
    >>> ts = autoai_ts_libs.deps.tspy.time_series([0, 1], granularity, start_time)
    >>> ts
    TimeStamp: 1990-07-06T00:00Z     Value: 0
    TimeStamp: 1990-07-07T00:00Z     Value: 1
    """
    j_list = tsc.java_bridge.convert_to_java_list(list_of_values)

    if granularity is None and start_time is None:

        return TimeSeries(
            tsc,
            tsc.packages.time_series.core.timeseries.TimeSeries.list(j_list)
        )
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        trs = TRS(tsc, granularity, start_time)
        return TimeSeries(
            tsc,
            tsc.packages.time_series.core.timeseries.TimeSeries.list(
                j_list,
                trs._j_trs
            ),
            trs
        )


def _reader(tsc, time_series_reader, granularity=None, start_time=None):
    """
    create a time-series from a time-series reader

    Parameters
    ----------
    time_series_reader : :class:`~autoai_ts_libs.deps.tspy.io.TimeSeriesReader`
        the time-series reader
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries
        a new time-series
    """
    if granularity is None and start_time is None:
        return TimeSeries(
            tsc,
            tsc.packages.time_series.core.timeseries.TimeSeries.reader(
                tsc.java_bridge.java_implementations.TimeSeriesReader(time_series_reader)
            )
        )
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        trs = TRS(tsc, granularity, start_time)
        return TimeSeries(
            tsc,
            tsc.packages.time_series.core.timeseries.TimeSeries.reader(
                tsc.java_bridge.java_implementations.JavaTimeSeriesReader(time_series_reader),
                trs._j_trs
            ),
            trs
        )


def _df(tsc, df, ts_column=None, value_column=None, granularity=None, start_time=None):
    """
    create a time-series from a pandas dataframe

    Parameters
    ----------
    df : pandas dataframe
        the pandas dataframe to convert to a time-series
    ts_column : string, optional
        the name of the column containing timestamps used in retrieving timestamps
        (default is using timestamps based on record index)
    value_column : string or list, optional
        the name of the column containing values used in retrieving values (default is create value using all columns)
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries
        a new time-series

    Examples
    --------
    create a simple pandas dataframe

    >>> import numpy as np
    >>> import pandas as pd
    >>> data = np.array([['', 'key', 'timestamp', "value"],\
                     ['', "a", 1, 27],\
                     ['', "b", 3, 4],\
                     ['', "a", 5, 17],\
                     ['', "a", 3, 7],\
                     ['', "b", 2, 45]\
                    ])
    >>> df = pd.DataFrame(data=data[1:, 1:],\
                      index=data[1:, 0],\
                      columns=data[0, 1:]).astype(dtype={'key': 'object', 'timestamp': 'int64', 'value': 'float64'})
    >>> df
    key  timestamp  value
      a          1   27.0
      b          3    4.0
      a          5   17.0
      a          3    7.0
      b          2   45.0

    create a time-series from a dataframe specifying a timestamp and value column

    >>> ts = autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp", value_column="value")
    >>> ts
    TimeStamp: 1     Value: 27.0
    TimeStamp: 2     Value: 45.0
    TimeStamp: 3     Value: 4.0
    TimeStamp: 3     Value: 7.0
    TimeStamp: 5     Value: 17.0

    create a time-series from a dataframe specifying only a timestamp column

    >>> ts = autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp")
    >>> ts
    TimeStamp: 1     Value: {value=27.0, key=a}
    TimeStamp: 2     Value: {value=45.0, key=b}
    TimeStamp: 3     Value: {value=4.0, key=b}
    TimeStamp: 3     Value: {value=7.0, key=a}
    TimeStamp: 5     Value: {value=17.0, key=a}

    create a time-series from a dataframe specifying no timestamp or value column

    >>> ts = autoai_ts_libs.deps.tspy.time_series(df)
    >>> ts
    TimeStamp: 0     Value: {value=27.0, key=a, timestamp=1}
    TimeStamp: 1     Value: {value=4.0, key=b, timestamp=3}
    TimeStamp: 2     Value: {value=17.0, key=a, timestamp=5}
    TimeStamp: 3     Value: {value=7.0, key=a, timestamp=3}
    TimeStamp: 4     Value: {value=45.0, key=b, timestamp=2}

    create a time-series from a dataframe specifying a timestamp column and using a time-reference-system

    >>> import datetime
    >>> start_time = datetime.datetime(1990, 7, 6)
    >>> granularity = datetime.timedelta(weeks=1)
    >>> ts = autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp", granularity=granularity, start_time=start_time)
    >>> ts
    TimeStamp: 1990-07-13T00:00Z     Value: {value=27.0, key=a}
    TimeStamp: 1990-07-20T00:00Z     Value: {value=45.0, key=b}
    TimeStamp: 1990-07-27T00:00Z     Value: {value=4.0, key=b}
    TimeStamp: 1990-07-27T00:00Z     Value: {value=7.0, key=a}
    TimeStamp: 1990-08-10T00:00Z     Value: {value=17.0, key=a}
    """
    import simplejson
    response = df.to_dict('records')

    json_str = simplejson.dumps(response, ignore_nan=False, default=lambda o: list(o)) # <-- should be used?
    keys = df.keys()
    keys_dict = {k: str(df[k].dtype) for k in keys}

    if granularity is None and start_time is None:
        trs = None
        j_trs = None
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        trs = TRS(tsc, granularity, start_time)
        j_trs = trs._j_trs

    if value_column is None or isinstance(value_column, list):

        if ts_column is None:
            if isinstance(value_column, list):
                keys_dict = {k: v for k, v in keys_dict.items() if k in value_column}

            j_keys_dict = tsc.packages.java.util.HashMap()
            for k, v in keys_dict.items():
                j_keys_dict.put(k, v)
            return TimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    None,
                    j_keys_dict,
                    j_trs
                ),
                trs
            )
        else:
            ts_pair = tsc.packages.time_series.core.utils.Pair(ts_column, keys_dict[ts_column])
            keys_dict.pop(ts_column)
            if isinstance(value_column, list):
                keys_dict = {k: v for k, v in keys_dict.items() if k in value_column if k != ts_column}
            return TimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    ts_pair,
                    tsc.java_bridge.convert_to_java_map(keys_dict),
                    j_trs
                ),
                trs
            )
    else:

        if ts_column is None:
            return TimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    None,
                    tsc.packages.time_series.core.utils.Pair(value_column, keys_dict[value_column]),
                    j_trs
                ),
                trs
            )
        else:
            return TimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    tsc.packages.time_series.core.utils.Pair(ts_column, keys_dict[ts_column]),
                    tsc.packages.time_series.core.utils.Pair(value_column, keys_dict[value_column]),
                    j_trs
                ),
                trs
            )


def time_series(*args, **kwargs):
    """creates a single-time-series object

    Parameters
    ----------
    data:
        type `list` or `pandas.DataFrame` or `TimeSeriesReader` or `ObservationCollection`

        * `list`
        * :class:`~pandas.DataFrame`
        * :class:`~autoai_ts_libs.deps.tspy.data_structures.io.TimeSeriesReader.TimeSeriesReader`
        * :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`

    ts_func : func, optional=None
        (only use when `data` is a `list`) if used, it is the function to combine duplicate time-ticks (default is do not combine)

    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    ts_column : string, optional
        (only use with `data` is a `pd.DataFrame`)
        the name of the column containing timestamps used in retrieving timestamps
        (default is using timestamps based on record index)

    value_column : string or list, optional
        (only use with `data` is a `pd.DataFrame`)
        the name of the column containing values used in retrieving values (default is create value using all columns)

    Returns
    -------
    :class:`.TimeSeries`
        a new time-series

    Raises
    --------
    ValueError
        If there is an error in the input arguments, e.g. not a supporting data type

    Examples
    --------

    * create a simple pandas dataframe

    >>> import numpy as np
    >>> import pandas as pd
    >>> data = np.array([['', 'key', 'timestamp', "value"],\
                     ['', "a", 1, 27],\
                     ['', "b", 3, 4],\
                     ['', "a", 5, 17],\
                     ['', "a", 3, 7],\
                     ['', "b", 2, 45]\
                    ])
    >>> df = pd.DataFrame(data=data[1:, 1:],\
                      index=data[1:, 0],\
                      columns=data[0, 1:]).astype(dtype={'key': 'object', 'timestamp': 'int64', 'value': 'float64'})
    >>> df
    key  timestamp  value
      a          1   27.0
      b          3    4.0
      a          5   17.0
      a          3    7.0
      b          2   45.0

    create a time-series from a dataframe specifying a timestamp and value column

    >>> ts = autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp", value_column="value")
    >>> ts
    TimeStamp: 1     Value: 27.0
    TimeStamp: 2     Value: 45.0
    TimeStamp: 3     Value: 4.0
    TimeStamp: 3     Value: 7.0
    TimeStamp: 5     Value: 17.0

    create a time-series from a dataframe specifying only a timestamp column - it will uses all other columns and stores as value
    as a single dictionary.

    >>> ts = autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp")
    >>> ts
    TimeStamp: 1     Value: {value=27.0, key=a}
    TimeStamp: 2     Value: {value=45.0, key=b}
    TimeStamp: 3     Value: {value=4.0, key=b}
    TimeStamp: 3     Value: {value=7.0, key=a}
    TimeStamp: 5     Value: {value=17.0, key=a}

    create a time-series from a dataframe specifying no timestamp or value column

    >>> ts = autoai_ts_libs.deps.tspy.time_series(df)
    >>> ts
    TimeStamp: 0     Value: {value=27.0, key=a, timestamp=1}
    TimeStamp: 1     Value: {value=4.0, key=b, timestamp=3}
    TimeStamp: 2     Value: {value=17.0, key=a, timestamp=5}
    TimeStamp: 3     Value: {value=7.0, key=a, timestamp=3}
    TimeStamp: 4     Value: {value=45.0, key=b, timestamp=2}

    create a time-series from a dataframe specifying a timestamp column and using a time-reference-system

    >>> import datetime
    >>> start_time = datetime.datetime(1990, 7, 6)
    >>> granularity = datetime.timedelta(weeks=1)
    >>> ts = autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp", granularity=granularity, start_time=start_time)
    >>> ts
    TimeStamp: 1990-07-13T00:00Z     Value: {value=27.0, key=a}
    TimeStamp: 1990-07-20T00:00Z     Value: {value=45.0, key=b}
    TimeStamp: 1990-07-27T00:00Z     Value: {value=4.0, key=b}
    TimeStamp: 1990-07-27T00:00Z     Value: {value=7.0, key=a}
    TimeStamp: 1990-08-10T00:00Z     Value: {value=17.0, key=a}


    * create a time-series from a list of values

    >>> ts = autoai_ts_libs.deps.tspy.time_series([0, 1])
    >>> ts
    TimeStamp: 0     Value: 0
    TimeStamp: 1     Value: 1

    create a time-series from a list of values with a time-reference system

    >>> import datetime
    >>> granularity = datetime.timedelta(days=1)
    >>> start_time = datetime.datetime(1990,7,6)
    >>> ts = autoai_ts_libs.deps.tspy.time_series([0, 1], granularity=granularity, start_time=start_time)
    >>> ts
    TimeStamp: 1990-07-06T00:00Z     Value: 0
    TimeStamp: 1990-07-07T00:00Z     Value: 1

    * create a collection of observations

    >>> import autoai_ts_libs.deps.tspy
    >>> observations = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(0,0)).add(autoai_ts_libs.deps.tspy.observation(1,1)).result()
    >>> observations
    [(0,0),(1,1)]

    create a time-series from observations

    >>> ts = autoai_ts_libs.deps.tspy.time_series(observations)
    >>> ts
    TimeStamp: 0     Value: 0
    TimeStamp: 1     Value: 1

    create a time-series from observations with a time-reference system

    >>> import datetime
    >>> granularity = datetime.timedelta(days=1)
    >>> start_time = datetime.datetime(1990,7,6)
    >>> ts = autoai_ts_libs.deps.tspy.time_series(observations, granularity=granularity, start_time=start_time)
    >>> ts
    TimeStamp: 1990-07-06T00:00Z     Value: 0
    TimeStamp: 1990-07-07T00:00Z     Value: 1
    """

    tsc = _get_context()
    data = args[0]
    def _validate_args():
      if 'ts_func' in kwargs and not isinstance(data, list):
        msg = "`ts_func` is being used with incompatible data: must be a list"
        log.error(msg)
        raise ValueError(msg)
      if 'ts_column' in kwargs and not isinstance(data, pd.DataFrame):
        msg = "`ts_column` is being used with incompatible data: must be a pandas.DataFrame"
        log.error(msg)
        raise ValueError(msg)
      if 'value_column' in kwargs and not isinstance(data, pd.DataFrame):
        msg = "`value_column` is being used with incompatible data: must be a pandas.DataFrame"
        log.error(msg)
        raise ValueError(msg)

    _validate_args()
    if isinstance(data, pd.DataFrame):
        return _df(tsc, *args, **kwargs)
    elif isinstance(data, list):
        return _list(tsc, *args, **kwargs)
    elif isinstance(data, TimeSeriesReader):
        return _reader(tsc, *args, **kwargs)
    elif isinstance(data, BoundTimeSeries):
        return _observations(tsc, *args, **kwargs)
