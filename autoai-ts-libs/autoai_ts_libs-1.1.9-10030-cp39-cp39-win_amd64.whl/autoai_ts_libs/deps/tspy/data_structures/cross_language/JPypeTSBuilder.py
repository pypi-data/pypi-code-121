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
from autoai_ts_libs.deps.tspy.data_structures.observations.TSBuilder import TSBuilder
from autoai_ts_libs.deps.tspy.data_structures.observations.Segment import Segment
from autoai_ts_libs.deps.tspy.data_structures.forecasting.Prediction import Prediction


class JPypeTSBuilder(TSBuilder):

    """
    a mutable builder for creating an :class:`.ObservationCollection`
    """
    def __init__(self, tsc):
        super().__init__(tsc)
        self._j_builder = tsc.packages.time_series.core.utils.TSBuilder()

    def add(self, observation):
        """adds an observation to the builder

        Parameters
        ----------
        observation : :class:`.Observation`, tuple
            the observation or tuple(time_tick, value) to add

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        if isinstance(observation, tuple):
            self._j_builder.add(observation[0], self._tsc.java_bridge.cast_to_j_if_necessary(observation[1]))
        else:
            self._j_builder.add(observation._j_observation)
        return self

    def __len__(self):
        return self._j_builder.size()

    def result(self, granularity=None, start_time=None):
        """
        get an bounded timeseries from the observations in this builder

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
        start_time : datetime, optional
            the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

        Returns
        -------
        :class:`.BoundTimeSeries`
            a new bound timeseries
        """
        if granularity is None and start_time is None:
            j_trs = None
        else:
            import datetime
            from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            j_trs = TRS(self._tsc, granularity, start_time)

        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries
        if j_trs is None:
            return BoundTimeSeries(self._tsc, self._j_builder.result())
        else:
            return BoundTimeSeries(self._tsc, self._j_builder.result(j_trs))


    def clear(self):
        """
        clear the observations in this builder

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        self._j_builder.clear()
        return self

    def is_empty(self):
        """checks if there is any observation

        Returns
        -------
        bool
            True if no observations exist in this builder, otherwise false
        """
        return self._j_builder.isEmpty()

    def add_all(self, observations):
        """
        add all observations in an observation-collection to this builder

        Parameters
        ----------
        observations : :class:`.ObservationCollection` or list
            the observations or list of tuple(time_tick, value) to add

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
        if isinstance(observations[0], Observation):
            for o in observations:
                self.add(o)
        else:
            for o in observations:
                self.add((o[0], o[1]))

        return self
