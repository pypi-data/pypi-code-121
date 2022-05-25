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
from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries


class SegmentTimeSeries(TimeSeries):
    """
    A special form of time-series that consists of observations with a value of type :class:`~autoai_ts_libs.deps.tspy.data_structures.Segment.Segment`
    """

    def __init__(self, tsc, j_ts, trs=None):
        super().__init__(tsc, j_ts, trs)
        self._tsc = tsc
        self._j_segment_ts = j_ts

    def cache(self, cache_size=None):
        if cache_size is None:
            j_seg_ts = self._j_segment_ts.cache()
        else:
            j_seg_ts = self._j_segment_ts.cache(cache_size)

        return SegmentTimeSeries(
            self._tsc,
            j_seg_ts,
            self._trs
        )

    def map(self, func):
        if hasattr(func, '__call__'):
            func = self._tsc.java_bridge.java_implementations.UnaryMapFunction(func)

        return TimeSeries(
            self._tsc,
            self._j_segment_ts.map(func),
            self._trs
        )

    def flatmap(self, func):
        return TimeSeries(
            self._tsc,
            self._j_segment_ts.flatMap(self._tsc.java_bridge.java_implementations.UnaryMapFunction(func)),
            self._trs
        )
