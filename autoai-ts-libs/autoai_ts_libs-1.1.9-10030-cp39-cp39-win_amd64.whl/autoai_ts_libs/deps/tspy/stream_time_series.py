"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries.StreamTimeSeries`
"""
from autoai_ts_libs.deps.tspy import _get_context

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
from autoai_ts_libs.deps.tspy.data_structures import TRS
from autoai_ts_libs.deps.tspy.data_structures.io.PullStreamTimeSeriesReader import PullStreamTimeSeriesReader
from autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries import StreamTimeSeries
import datetime

def reader(stream_reader, granularity=None, start_time=None):
    """
    create a stream-time-series from a stream-time-series-reader

    Parameters
    ----------
    stream_time_series_reader : :class:`~autoai_ts_libs.deps.tspy.data_structures.io.PullStreamTimeSeriesReader.PullStreamTimeSeriesReader` or :class:`~autoai_ts_libs.deps.tspy.data_structures.io.PushStreamTimeSeriesReader.PushStreamTimeSeriesReader`
        a user-implemented stream-time-series-reader
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries.StreamTimeSeries`
        a new stream-time-series
    """
    tsc = _get_context()
    if isinstance(stream_reader, PullStreamTimeSeriesReader):
        py_reader = tsc.java_bridge.java_implementations.JavaPullStreamTimeSeriesReader(stream_reader)
    else:
        py_reader = tsc.java_bridge.java_implementations.JavaPushStreamTimeSeriesReader(stream_reader)

    if granularity is None and start_time is None:
        return StreamTimeSeries(
            tsc,
            tsc.packages.time_series.streaming.timeseries.StreamTimeSeries.reader(py_reader)
        )
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        trs = TRS(tsc, granularity, start_time)
        return StreamTimeSeries(
            tsc,
            tsc.packages.time_series.streaming.timeseries.StreamTimeSeries.reader(
                py_reader,
                trs._j_trs
            ),
            trs
        )


def text_file(path, map_func, granularity=None, start_time=None):
    """
    create a stream-time-series from a text file

    Parameters
    ----------
    path : string
        path to file
    map_func : func
        function from a single line of a file to an :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.Observation.Observation` or None
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries.StreamTimeSeries`
        a new stream-time-series
    """
    tsc = _get_context()
    if granularity is None and start_time is None:
        return StreamTimeSeries(
            tsc,
            tsc.packages.time_series.streaming.timeseries.StreamTimeSeries.textFile(
                path,
                tsc.java_bridge.java_implementations.UnaryMapFunctionResultingInOptional(map_func)
            )
        )
    else:
        if granularity is None:
            granularity = datetime.timedelta(milliseconds=1)
        if start_time is None:
            start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        trs = TRS(tsc, granularity, start_time)

        return StreamTimeSeries(
            tsc,
            tsc.packages.time_series.streaming.timeseries.StreamTimeSeries.textFile(
                path,
                tsc.java_bridge.java_implementations.UnaryMapFunctionResultingInOptional(map_func),
                trs._j_trs
            ),
            trs
        )


def queue(observation_queue, granularity=None, start_time=None):
    """
    create a stream-time-series from a queue of observations

    Parameters
    ----------
    observation_queue : queue.Queue
        queue of :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.Observation.Observation`
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries.StreamTimeSeries`
        a new stream-time-series

    Examples
    --------
    create a simple queue

    >>> import queue
    >>> observation_queue = queue.Queue()

    create a simple stream-time-series from a queue

    >>> import autoai_ts_libs.deps.tspy
    >>> sts = autoai_ts_libs.deps.tspy.stream_time_series.queue(observation_queue)
    """
    from autoai_ts_libs.deps.tspy.data_structures.io.PythonQueueStreamTimeSeriesReader import PythonQueueStreamTimeSeriesReader
    return reader(PythonQueueStreamTimeSeriesReader(observation_queue), granularity, start_time)
