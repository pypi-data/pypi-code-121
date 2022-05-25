
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

class UpdatableAnomalyDetector:
    """
    An updatable anomaly detector which used in conjunction with a
    :class:`~autoai_ts_libs.deps.tspy.forecasting.ForecastingModel.ForecastingModel` can identify anomalies
    """
    def __init__(self, tsc, j_anomaly_detector):
        self._tsc = tsc
        self._j_anomaly_detector = j_anomaly_detector

    def __getstate__(self):
        if self._tsc.java_bridge.is_instance_of_java_class(
                self._j_anomaly_detector,
                "com.ibm.research.time_series.forecasting.anomaly.pointwise.BoundedAnomalyDetector"):
            j_fm_str = self._tsc.packages.time_series.transforms.forecastors.PythonConnector \
                .serializeUpdatableAnomalyDetector(self._j_anomaly_detector)
            return {'type': 'point_wise', 'j_anomaly_detector': str(j_fm_str)}
        else:
            j_fm_str = self._tsc.packages.time_series.transforms.forecastors.PythonConnector \
                .serializeWindowedAnomalyDetector(self._j_anomaly_detector)
            return {'type': 'windowed', 'j_anomaly_detector': str(j_fm_str)}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        self._tsc = get_or_create()
        if d['type'] == 'point_wise':
            self._j_anomaly_detector = self._tsc.packages.time_series.transforms.forecastors.PythonConnector\
                .deserializeUpdatableAnomalyDetector(d['j_anomaly_detector'])
        else:
            self._j_anomaly_detector = self._tsc.packages.time_series.transforms.forecastors.PythonConnector\
                .deserializeWindowedAnomalyDetector(d['j_anomaly_detector'])

    def is_anomaly(self, timestamp, value):
        """
        check for an anomaly given a timestamp, and a value

        Parameters
        ----------
        timestamp : int
            the point in time for which the actual value corresponds
        value : float
            the data value under consideration as an anomaly

        Returns
        -------
        bool
            true if the value is outside of the bounds identified for the given time using the instance's confidence
            level or the value is NaN, otherwise false
        """
        return self._j_anomaly_detector.isAnomaly(timestamp, value)

    def reset_detector(self):
        """
        Reset the model being used by this instance.
        """
        self._j_anomaly_detector.resetDetector()

    def __str__(self):
        return str(self._j_anomaly_detector.toString())

    def __repr__(self):
        return self.__str__()
