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

import abc

class PullStreamTimeSeriesReader(metaclass = abc.ABCMeta):
    """
    interface to represent reading stream-time-series data at motion from a data-source where data is being pulled to
    the reader
    """

    def __init__(self):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        self._tsc = get_or_create()
        self._j_reader = self._tsc.packages.time_series.streaming.io.PythonPullStreamTimeSeriesReader(
            self._tsc.java_bridge.java_implementations.UnaryMapFunctionResultingInOptional(self._tsc, self.parse),
            self._tsc.java_bridge.java_implementations.IteratorMessageSupplier(self._tsc, self.poll)
        )

    def _parse(self, message):
        return self._j_reader.parse(message)

    def _read(self):
        return self._j_reader.read()

    @abc.abstractmethod
    def parse(self, message):
        """
        parse a message

        Parameters
        ----------
        message : Any
            a message

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
            a single observation or None if parsing has failed
        """
        return

    @abc.abstractmethod
    def poll(self):
        """
        poll for the latest list of messages from your source

        Returns
        -------
        list
            a list of messages
        """
        return
