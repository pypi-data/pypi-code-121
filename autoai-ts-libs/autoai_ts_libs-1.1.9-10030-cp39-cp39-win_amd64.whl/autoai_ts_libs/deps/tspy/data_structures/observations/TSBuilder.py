import abc

class TSBuilder(object, metaclass = abc.ABCMeta):

    def __init__(self, tsc):
        self._tsc = tsc

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def clear(self):
        """
        clear the observations in this builder

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        pass

    @abc.abstractmethod
    def is_empty(self):
        """checks if there is any observation

        Returns
        -------
        bool
            True if no observations exist in this builder, otherwise false
        """
        pass

    @abc.abstractmethod
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
        pass
