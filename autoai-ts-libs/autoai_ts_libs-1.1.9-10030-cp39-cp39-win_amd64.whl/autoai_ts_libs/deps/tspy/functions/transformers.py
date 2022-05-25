"""
main entry point for all transformers (given time-series, return new time-series)
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
from autoai_ts_libs.deps.tspy import _get_context


def z_score(mean=None, sd=None):
    """map each value to a number of standard deviations above/below the mean

    Parameters
    ----------
    mean : float, optional
        the mean to use when performing z-score (default is mean of input series)
    sd : float, optional
        the standard-deviation when performing z-score (default is sd of input series)
    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a Z-Normalization transform which, when applied on a numeric time-series will map each value to a number of
        standard deviations above/below the mean
    """
    tsc = _get_context()
    if mean is None and sd is None:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.zscore()
    elif mean is not None or sd is not None:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.zscore(mean, sd)
    else:
        from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage
        raise TSErrorWithMessage("mean and sd must either both be none or both be specified")

def z_score_with_annotation():
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.zscoreWithAnnotation()


def difference():
    """take the difference between the current observation value and its previous observation value

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a difference transform which, when applied on a numeric time-series will take the difference between the
        current observation value and its previous observation value
    """
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.difference()


def detect_anomalies(forecasting_model, confidence, update_model=False, info=False):
    """filter for anomalies within the time-series given a forecasting model and its definition of confidence intervals

    Parameters
    ----------
    forecasting_model : ~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel
        the forecasting model to use
    confidence : float
        a number between 0 and 1 (exclusive) which are used to determine the confidence interval
    update_model : bool, optional
        if True, the model will be trained/updated (default is False)
    info : bool, optional
        if True, will give back the bounds/errors/expected values, otherwise no other information will be provided
        (default is False)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        an anomaly detection transform which, when applied on a time-series filter for anomalies within the time-series
        given a forecasting model and its definition of confidence intervals
    """
    tsc = _get_context()
    if info:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.detectAnomaliesWithInfo(
            forecasting_model._j_fm,
            confidence,
            update_model
        )
    else:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.detectAnomalies(
            forecasting_model._j_fm,
            confidence,
            update_model
        )


def awgn(mean=None, sd=None):
    """add noise using the following method https://en.wikipedia.org/wiki/Additive_white_Gaussian_noise

    Parameters
    ----------
    mean : float, optional
        the mean around which to add the noise (default is time-series mean)
    sd : float, optional
        the standard deviation to use (default is time-series standard deviation)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        an additive-white-gaussian noise transform which, when applied on a time-series will add noise using the
        following method https://en.wikipedia.org/wiki/Additive_white_Gaussian_noise
    """
    tsc = _get_context()
    if mean is None and sd is None:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.awgn()
    elif sd is None:
        j_sd = tsc.packages.java.lang.Double.NaN
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.awgn(mean, j_sd)
    elif mean is None:
        j_mean = tsc.packages.java.lang.Double.NaN
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.awgn(j_mean, sd)
    else:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.awgn(mean, sd)


def mwgn(mean=None):
    """add noise given a standard-deviation

    Parameters
    ----------
    sd : float, optional
        the standard deviation to use (default is time-series standard deviation)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        an multiplicative-white-gaussian noise transform which, when applied on a time-series will add noise given a
        standard-deviation
    """
    tsc = _get_context()
    if mean is None:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.mwgn()
    else:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.mwgn(mean)


def ljung_box(window, step, num_lags, period):
    """test for the absence of serial correlation, up to a specified lag

    Parameters
    ----------
    window : int
        length of window
    step : int
        number of steps
    num_lags : int
        number of lags
    period : int
        number to multiply the lag by when getting windows

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a ljung-box transform, which applied on a time-series will test for the absence of serial correlation,
        up to a specified lag
    """
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.stats.StatTransformers.ljungBox(
        window,
        step,
        num_lags,
        period
    )

def remove_consecutive_duplicate_values():
    """trim the time-series by removing consecutive duplicate values

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a remove-consecutive-duplicates transform, which applied on a time-series will trim the time-series by removing
        consecutive duplicate values
    """
    tsc = _get_context()
    return tsc.packages.time_series.core.core_transforms.duplicate.DuplicateTransformers.removeConsecutiveDuplicateValues()

def combine_duplicate_time_ticks(combine_strategy):
    """combine the observations which have the same time-tick

    Parameters
    ----------
    combine_strategy : func
        a function or lamdba that receives one argument representing the collection of values of the same timestamp and
        returns a single value

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a combine-duplicate-time-ticks transform, which applied on a time-series will combine the observations which
        have the same time-tick
    """
    tsc = _get_context()
    if hasattr(combine_strategy, '__call__'):
        return tsc.packages.time_series.core.core_transforms.duplicate.DuplicateTransformers.combineDuplicateTimeTicks(
            tsc.java_bridge.java_implementations.UnaryMapFunction(combine_strategy)
        )
    else:
        return tsc.packages.time_series.core.core_transforms.duplicate.DuplicateTransformers.combineDuplicateTimeTicks(
            combine_strategy)


def paa(m):
    """approximate the time-series in a piecewise fashion. This is used to accelerate similarity measures between two
    time-series

    Parameters
    ----------
    m : int
        num buckets

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a piecewise-aggregate-approximation transform, which applied on a time-series will approximate the time-series
        in a piecewise fashion. This is used to accelerate similarity measures between two time-series
    """
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.paa(m)

def sax(min_value, max_value, num_bins):
    """transform the time-series to a time-series of symbols by discretizing the value. Discretization is performed by
    uniformly dividing the values between min_value and max_value into num_bins bins

    Parameters
    ----------
    min_value : float
        min value
    max_value : float
        max value
    num_bins : int
        number of bins

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a symbolic-aggregate-approximation transform, which applied on a time-series will transform the time-series to
        a time-series of symbols by discretizing the value
    """
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.sax(min_value, max_value, num_bins)

def ema(smoothing_constant):
    """smooth the time-series (x) such that the i^th observation on the transformed time-series
    y(t) = y(t-1) + (x(t) - y(t-1)) * (1 - smoothing_constant)

    Parameters
    ----------
    smoothing_constant : float
        a number between 0 and 1, the closer to 0, the faster the number will converge

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a exponentially-weighted-moving-average transform, which applied on a time-series (x) will smooth the
        time-series such that the i^th observation on the transformed time-series y(t) = y(t-1) + (x(t) - y(t-1)) *
        (1 - smoothing_constant)
    """
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.ema(smoothing_constant)

def decompose(samples_per_season, multiplicative):
    """get the residuals, trend, and seasonal components of a time-series

    Parameters
    ----------
    samples_per_season : int
        number of samples in a season
    multiplicative : bool
        if True, use multiplicative method, otherwise use additive

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a decomposition transform, which applied on a time-series will result in the residuals, trend, and seasonal
        components
    """
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.PythonMathTransformers.decompose(
        samples_per_season,
        multiplicative
    )

def discrete_cosine():
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.discreteCosine()

def fit_regression(periodicity):
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.fitRegression(periodicity)

def min_max_scaler(min_value=None, max_value=None):
    tsc = _get_context()
    if min_value is None and max_value is None:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.minMaxScaler()
    elif min_value is not None or max_value is not None:
        return tsc.packages.time_series.transforms.transformers.math.MathTransformers.minMaxScaler(
            min_value, max_value)
    else:
        from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage
        raise TSErrorWithMessage("min_value and max_value must either both be none or both be specified")


def min_max_scaler_with_annotation():
    tsc = _get_context()
    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.minMaxScalerWithAnnotation()


def moving_avg_peak_trough(window, threshold, influence, peaks="PEAK_AND_TROUGH"):
    """ transform the time-series to a time-series of 1, -1 and 0, where 1, -1, 0 represents peak,
    trough and normal respectively. The transformation is performed using moving average, moving
    standard deviation and z-score computed using them.

    Parameters
    ----------
    window : int
        the number of data points for computing moving average and moving standard deviation
    threshold : float
        threshold for z-score
    influence : float
        the influence of a data point where a peak or trough is detected in computing
        moving average and moving standard deviation
    peaks: str, optional
        enum to denote which of peaks / troughs to detect. One of PEAK, TROUGH, PEAK_AND_TROUGH (default is
        "PEAK_AND_TROUGH")


    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a moving average and standard deviation, z-score based peak trough transform, which applied on a time-series will transform the time-series to
        a time-series of symbols, consisting of 1, -1 and 0
    """
    tsc = _get_context()
    peaks = peaks.lower()

    if peaks == "peak":
        j_peaks = tsc.packages.time_series.transforms.transformers.math.utils.Peaks.PEAK
    elif peaks == "trough":
        j_peaks = tsc.packages.time_series.transforms.transformers.math.utils.Peaks.TROUGH
    else:
        j_peaks = tsc.packages.time_series.transforms.transformers.math.utils.Peaks.PEAK_AND_TROUGH

    return tsc.packages.time_series.transforms.transformers.math.MathTransformers.movingAvgPeakTrough(
        window, threshold, influence, j_peaks)

