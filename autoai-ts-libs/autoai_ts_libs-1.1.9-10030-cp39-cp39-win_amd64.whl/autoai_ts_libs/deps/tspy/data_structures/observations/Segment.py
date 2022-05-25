import sys

from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries


class Segment(BoundTimeSeries):
    """
    A special form of observation-collection which holds additional information as to how the segment was created.
    Segments are usually created through the use of a segmentation transform.

    Attributes
    ----------
    start : int
        start time-tick of window at instantiation time
    end : int
        end time-tick of window at instantiation time

    Notes
    -----
    a segments start/end need not equal its first/last time-tick
    """

    def __init__(self, tsc, j_observations, start=None, end=None):
        super().__init__(tsc, j_observations)
        self._j_observations = j_observations
        self._tsc = tsc
        if start is None and end is None:
            self._j_segment = self._tsc.packages.time_series.core.utils.Segment.fromSeries(j_observations)
        elif start is None or end is None:
            raise Exception("if start is none, end must be none and vice versa")
        else:
            self._j_segment = self._tsc.packages.time_series.core.utils.Segment.fromSeries(start, end,
                                                                                  j_observations)
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries
        self._observations = BoundTimeSeries(self._tsc, j_observations)
        if self._observations.is_empty():
            self._start = -sys.maxsize - 1
            self._end = sys.maxsize
        else:
            self._start = self._j_segment.start()
            self._end = self._j_segment.end()

    @property
    def observations(self):
        """
        Returns
        -------
        :class:`.ObservationCollection`
            the underlying collection of observations in this segment
        """
        return self._observations

    @property
    def start(self):
        """
        Returns
        -------
        int
            start time-tick of window at instantiation time
        """
        return self._start

    @property
    def end(self):
        """
        Returns
        -------
        int
            end time-tick of window at instantiation time
        """
        return self._end

    def toString(self):
        return self._j_segment.toString()

    def __eq__(self, other):
        return self._j_segment.equals(other._j_segment)

    def __str__(self):
        return self._j_segment.toString()
