"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
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
import logging
from autoai_ts_libs.deps.tspy import _get_context
from autoai_ts_libs.deps.tspy.data_structures import MultiTimeSeries
import datetime

log = logging.getLogger(__name__)


def _from_observations(tsc, list_key_observation_pairs):
    """
    create a multi-time-series from a list of tuples (key, observation)

    Parameters
    ----------
    list_key_observation_pairs : list
        list of (key, observations) tuples

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
        a new multi-time-series

    Notes
    -----
    each time-series will be created from a group by operation on the key.

    Examples
    --------
    create a list of (key, observation) tuples

    >>> observations = [("a", autoai_ts_libs.deps.tspy.observation(2,1)), ("b", autoai_ts_libs.deps.tspy.observation(1,8)), ("a", autoai_ts_libs.deps.tspy.observation(1,7)), ("b", autoai_ts_libs.deps.tspy.observation(4,6)), ("c", autoai_ts_libs.deps.tspy.observation(1,5))]
    >>> observations
    [('a', TimeStamp: 2     Value: 1), ('b', TimeStamp: 1     Value: 8), ('a', TimeStamp: 1     Value: 7), ('b', TimeStamp: 4     Value: 6), ('c', TimeStamp: 1     Value: 5)]

    create a multi-time-series from observations

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series(observations)
    >>> mts
    a time series
    ------------------------------
    TimeStamp: 1     Value: 7
    TimeStamp: 2     Value: 1
    b time series
    ------------------------------
    TimeStamp: 1     Value: 8
    TimeStamp: 4     Value: 6
    c time series
    ------------------------------
    TimeStamp: 1     Value: 5
    """
    return MultiTimeSeries(
        tsc,
        tsc.packages.time_series.core.timeseries.MultiTimeSeries.fromObservations(
            tsc.java_bridge.convert_to_java_list(
                tsc,
                list(map(
                    lambda tup: tsc.packages.time_series.core.utils.Pair(tup[0], tup[1]._j_observation),
                    list_key_observation_pairs
                ))
            )
        )
    )


def _df_instants(tsc, df, key_columns=None, ts_column=None, granularity=None, start_time=None):
    """
    create a multi-time-series from a pandas dataframe in instants format. Instants format is defined as each
    time-series key being a separate column of the dataframe.

    Parameters
    ----------
    df : pandas dataframe
        the dataframe to convert to a multi-time-series
    key_columns : list, optional
        columns to use in multi-time-series creation (default is all columns)
    ts_column : string, optional
        column name containing time-ticks (default is time-tick based on index into dataframe)
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
        a new multi-time-series

    Examples
    --------
    create a simple df with a single index

    >>> import numpy as np
    >>> import pandas as pd
    >>> data = np.array([['', 'letters', 'timestamp', "numbers"],
                 ...['', "a", 1, 27],
                 ...['', "b", 3, 4],
                 ...['', "a", 5, 17],
                 ...['', "a", 3, 7],
                 ...['', "b", 2, 45]
                ...])
    >>> df = pd.DataFrame(data=data[1:, 1:],
                  ...columns=data[0, 1:]).astype(dtype={'letters': 'object', 'timestamp': 'int64', 'numbers': 'float64'})
      letters  timestamp  numbers
    0       a          1     27.0
    1       b          3      4.0
    2       a          5     17.0
    3       a          3      7.0
    4       b          2     45.0

    create a multi-time-series from a df using instants format

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series.df_instants(df, ts_column='timestamp')
    >>> mts
    numbers time series
    ------------------------------
    TimeStamp: 1     Value: 27.0
    TimeStamp: 2     Value: 45.0
    TimeStamp: 3     Value: 4.0
    TimeStamp: 3     Value: 7.0
    TimeStamp: 5     Value: 17.0
    letters time series
    ------------------------------
    TimeStamp: 1     Value: a
    TimeStamp: 2     Value: b
    TimeStamp: 3     Value: b
    TimeStamp: 3     Value: a
    TimeStamp: 5     Value: a
    """
    keys = df.keys()
    keys_dict = {k: str(df[k].dtype) for k in keys}
    import simplejson

    response = df.to_dict()

    json_str = simplejson.dumps(response, ignore_nan=False, default=lambda o: int(o.timestamp() * 1e3))

    if granularity is None and start_time is None:
        trs = None
        j_trs = None
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
        trs = TRS(tsc, granularity, start_time)
        j_trs = trs._j_trs

    ts_index = None
    if ts_column is not None:
        ts_index = tsc.packages.time_series.core.utils.Pair(ts_column, keys_dict.get(ts_column))
        keys_dict.pop(ts_column)

    if key_columns is not None:
        keys_dict = {k: v for k, v in keys_dict.items() if k in key_columns}

    return MultiTimeSeries(
        tsc,
        tsc.packages.time_series.core.utils.PythonConnector.readDataFrameInstantsJsonString(
            json_str,
            ts_index,
            tsc.java_bridge.convert_to_java_map(keys_dict),
            j_trs
        )
    )


def _df_observations(tsc, df, key_column, ts_column=None, value_column=None, granularity=None, start_time=None):
    """
    create a multi-time-series from a pandas dataframe in observations format. Observations format is defined as each
    record in the dataframe having a key, where each time-series is created by grouping unique keys.

    Parameters
    ----------
    df : pandas dataframe
        the dataframe to convert to a multi-time-series
    key_column : string
        column name containing the key
    ts_column : string, optional
        column name containing time-ticks (default is time-tick based on index into dataframe)
    value_column : list or string, optional
        column name(s) containing values (default is all columns)
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
        a new multi-time-series

    Examples
    --------
    create a simple df with a single index

    >>> import numpy as np
    >>> import pandas as pd
    >>> data = np.array([['', 'letters', 'timestamp', "numbers"],
                 ...['', "a", 1, 27],
                 ...['', "b", 3, 4],
                 ...['', "a", 5, 17],
                 ...['', "a", 3, 7],
                 ...['', "b", 2, 45]
                ...])
    >>> df = pd.DataFrame(data=data[1:, 1:],
                  ...columns=data[0, 1:]).astype(dtype={'letters': 'object', 'timestamp': 'int64', 'numbers': 'float64'})
      letters  timestamp  numbers
    0       a          1     27.0
    1       b          3      4.0
    2       a          5     17.0
    3       a          3      7.0
    4       b          2     45.0

    create a multi-time-series from a df using observations format where the key is letters

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series.df_observations(df, key_column="letters", ts_column='timestamp')
    a time series
    ------------------------------
    TimeStamp: 1     Value: {numbers=27.0}
    TimeStamp: 3     Value: {numbers=7.0}
    TimeStamp: 5     Value: {numbers=17.0}
    b time series
    ------------------------------
    TimeStamp: 2     Value: {numbers=45.0}
    TimeStamp: 3     Value: {numbers=4.0}
    """
    keys = df.keys()
    keys_dict = {k: str(df[k].dtype) for k in keys}

    import simplejson

    response = df.to_dict(orient="records")

    json_str = simplejson.dumps(response, ignore_nan=False, default=lambda o: int(o.timestamp() * 1e3))

    key_pair = tsc.packages.time_series.core.utils.Pair(key_column, keys_dict[key_column])
    keys_dict.pop(key_column)

    if granularity is None and start_time is None:
        trs = None
        j_trs = None
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
        trs = TRS(tsc, granularity, start_time)
        j_trs = trs._j_trs

    if value_column is None or isinstance(value_column, list):

        if ts_column is None:
            if isinstance(value_column, list):
                keys_dict = {k: v for k, v in keys_dict.items() if k in value_column}
            return MultiTimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    key_pair,
                    None,
                    tsc.java_bridge.convert_to_java_map(keys_dict),
                    j_trs
                )
            )
        else:
            ts_pair = tsc.packages.time_series.core.utils.Pair(ts_column, keys_dict.get(ts_column))
            keys_dict.pop(ts_column)
            if isinstance(value_column, list):
                keys_dict = {k: v for k, v in keys_dict.items() if k in value_column}

            return MultiTimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    key_pair,
                    ts_pair,
                    tsc.java_bridge.convert_to_java_map(keys_dict),
                    j_trs
                )
            )
    else:
        value_pair = tsc.packages.time_series.core.utils.Pair(value_column, keys_dict.get(value_column))
        if ts_column is None:
            return MultiTimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    key_pair,
                    None,
                    value_pair,
                    j_trs
                )
            )
        else:
            ts_pair = tsc.packages.time_series.core.utils.Pair(ts_column, keys_dict.get(ts_column))
            keys_dict.pop(ts_column)
            return MultiTimeSeries(
                tsc,
                tsc.packages.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                    json_str,
                    key_pair,
                    ts_pair,
                    value_pair,
                    j_trs
                )
            )


def _dict(tsc, ts_dict, granularity=None, start_time=None):
    """
    create a time-series from a dict where the values are either collections of observations or time-series

    Parameters
    ----------
    ts_dict : dict
        dict where one key per :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
        a new multi-time-series

    Examples
    --------
    create a dict with observation-collection values

    >>> import autoai_ts_libs.deps.tspy
    >>> my_dict = {"ts1": autoai_ts_libs.deps.tspy.time_series([1,2,3]).materialize(), "ts2": autoai_ts_libs.deps.tspy.time_series([4,5,6]).materialize()}
    >>> my_dict
    {'ts1': [(0,1),(1,2),(2,3)], 'ts2': [(0,4),(1,5),(2,6)]}

    create a multi-time-series from dict without a time-reference-system

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series.dict(my_dict)
    >>> mts
    ts2 time series
    ------------------------------
    TimeStamp: 0     Value: 4
    TimeStamp: 1     Value: 5
    TimeStamp: 2     Value: 6
    ts1 time series
    ------------------------------
    TimeStamp: 0     Value: 1
    TimeStamp: 1     Value: 2
    TimeStamp: 2     Value: 3

    create a multi-time-series from dict containing a time-reference-system

    >>> import datetime
    >>> start_time = datetime.datetime(1990,7,6)
    >>> granularity = datetime.timedelta(days=1)
    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series.dict(my_dict, start_time=start_time, granularity=granularity)
    >>> mts
    ts2 time series
    ------------------------------
    TimeStamp: 1990-07-06T00:00Z     Value: 4
    TimeStamp: 1990-07-07T00:00Z     Value: 5
    TimeStamp: 1990-07-08T00:00Z     Value: 6
    ts1 time series
    ------------------------------
    TimeStamp: 1990-07-06T00:00Z     Value: 1
    TimeStamp: 1990-07-07T00:00Z     Value: 2
    TimeStamp: 1990-07-08T00:00Z     Value: 3
    """
    if granularity is None and start_time is None:
        trs = None
        j_trs = None
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
        trs = TRS(tsc, granularity, start_time)
        j_trs = trs._j_trs

    j_ts_map = tsc.packages.java.util.HashMap()
    for k, v in ts_dict.items():
        try:
            if trs is None:
                j_ts_map.put(k, v._j_ts)
            else:
                if v._j_ts.getTRS() is None:
                    raise Exception("your time series does not have a TRS and therefore cannot re-set the TRS")

                j_ts_map.put(k, v._j_ts.withTRS(j_trs))
        except:
            if trs is None:
                j_ts_map.put(k, tsc.packages.time_series.core.timeseries.TimeSeries.fromObservations(v._j_observations))
            else:
                j_ts_map.put(k, tsc.packages.time_series.core.timeseries.TimeSeries.fromObservations(v._j_observations,
                                                                                                     j_trs))

    return MultiTimeSeries(
        tsc,
        tsc.packages.time_series.core.timeseries.MultiTimeSeries(j_ts_map)
    )


def multi_time_series(*args, **kwargs):
    """creates a multi-time-series object

    Parameters
    ----------
    data:
        type `dict` or `pandas.DataFrame`, or :class:`~autoai_ts_libs.deps.tspy.data_structures.io.TimeSeriesReader.TimeSeriesReader` or :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`

        * dict where one key per :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`

        * dataframe: there are two way to convert to MTS, depending upon the use-cases,
        (1) group by values of a given column [e.g. temperature time series and a bunch of locations (keys)],
        (2) each column is turned into its own time-series [a single timestamp and multiple metrics, e.g. temperature and humidity columns]

    key_column : string
        (only use when `data` is a pandas's DataFrame and use-case (1))
        column name containing the key, each key value is used for grouping data into a single-time-series. IMPORTANT: `key_column` and `key_columns` are used exclusively.

    key_columns : list, optional
        (only use when `data` is a pandas's DataFrame and use-case (2))
        columns to use in multi-time-series creation (default is all columns), i.e. each column is turned into its own time-series component.
        IMPORTANT: `key_column` and `key_columns` are used exclusively.

    ts_column : string, optional
        (only use when `data` is a pandas's DataFrame)
        column name containing time-ticks (default: time-tick is based on index into dataframe)

    value_column : list or string, optional
        (only use when `data` is a pandas's DataFrame and use-case (1))
        column name(s) containing values (default is all columns)

    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)

    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
        a new multi-time-series

    Raises
    --------
    ValueError
        If there is an error in the input arguments, e.g. not a supporting data type

    Examples
    --------

    create a dict with observation-collection values

    >>> import autoai_ts_libs.deps.tspy
    >>> my_dict = {"ts1": autoai_ts_libs.deps.tspy.time_series([1,2,3]).materialize(), "ts2": autoai_ts_libs.deps.tspy.time_series([4,5,6]).materialize()}
    >>> my_dict
    {'ts1': [(0,1),(1,2),(2,3)], 'ts2': [(0,4),(1,5),(2,6)]}

    create a multi-time-series from dict without a time-reference-system

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series(my_dict)
    >>> mts
    ts2 time series
    ------------------------------
    TimeStamp: 0     Value: 4
    TimeStamp: 1     Value: 5
    TimeStamp: 2     Value: 6
    ts1 time series
    ------------------------------
    TimeStamp: 0     Value: 1
    TimeStamp: 1     Value: 2
    TimeStamp: 2     Value: 3

    * create a simple df with a single index

    >>> import numpy as np
    >>> import pandas as pd
    >>> data = np.array([['', 'letters', 'timestamp', "numbers"],
                 ...['', "a", 1, 27],
                 ...['', "b", 3, 4],
                 ...['', "a", 5, 17],
                 ...['', "a", 3, 7],
                 ...['', "b", 2, 45]
                ...])
    >>> df = pd.DataFrame(data=data[1:, 1:],
                  ...columns=data[0, 1:]).astype(dtype={'letters': 'object', 'timestamp': 'int64', 'numbers': 'float64'})
      letters  timestamp  numbers
    0       a          1     27.0
    1       b          3      4.0
    2       a          5     17.0
    3       a          3      7.0
    4       b          2     45.0

    create a multi-time-series from a df using instants format

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series(df, ts_column='timestamp')
    >>> mts
    numbers time series
    ------------------------------
    TimeStamp: 1     Value: 27.0
    TimeStamp: 2     Value: 45.0
    TimeStamp: 3     Value: 4.0
    TimeStamp: 3     Value: 7.0
    TimeStamp: 5     Value: 17.0
    letters time series
    ------------------------------
    TimeStamp: 1     Value: a
    TimeStamp: 2     Value: b
    TimeStamp: 3     Value: b
    TimeStamp: 3     Value: a
    TimeStamp: 5     Value: a

    * create a simple df with a single index

    >>> import numpy as np
    >>> import pandas as pd
    >>> data = np.array([['', 'letters', 'timestamp', "numbers"],
                 ...['', "a", 1, 27],
                 ...['', "b", 3, 4],
                 ...['', "a", 5, 17],
                 ...['', "a", 3, 7],
                 ...['', "b", 2, 45]
                ...])
    >>> df = pd.DataFrame(data=data[1:, 1:],
                  ...columns=data[0, 1:]).astype(dtype={'letters': 'object', 'timestamp': 'int64', 'numbers': 'float64'})
      letters  timestamp  numbers
    0       a          1     27.0
    1       b          3      4.0
    2       a          5     17.0
    3       a          3      7.0
    4       b          2     45.0

    create a multi-time-series from a df using observations format where the key is letters

    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series(df, key_column="letters", ts_column='timestamp')
    a time series
    ------------------------------
    TimeStamp: 1     Value: {numbers=27.0}
    TimeStamp: 3     Value: {numbers=7.0}
    TimeStamp: 5     Value: {numbers=17.0}
    b time series
    ------------------------------
    TimeStamp: 2     Value: {numbers=45.0}
    TimeStamp: 3     Value: {numbers=4.0}
    """
    tsc = _get_context()
    data = args[0]
    # key_column = args[1]
    if isinstance(data, pd.DataFrame):
        if len(args) == 2 or 'key_column' in kwargs:
            return _df_observations(tsc, *args, **kwargs)
        elif len(args) == 1:
            return _df_instants(tsc, *args, **kwargs)
        else:
            msg = "Argument errors: invalid arguments"
            log.error(msg)
            raise ValueError(msg)

    elif isinstance(data, dict):
        return _dict(tsc, *args, **kwargs)
    elif isinstance(data, list):
        return _from_observations(tsc, *args, **kwargs)
    else:
        msg = "Argument error: invalid arguments"
        raise ValueError(msg)
