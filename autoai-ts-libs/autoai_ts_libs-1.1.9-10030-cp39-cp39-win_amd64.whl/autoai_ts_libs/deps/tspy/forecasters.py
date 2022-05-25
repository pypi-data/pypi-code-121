"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`
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
from autoai_ts_libs.deps.tspy.data_structures.forecasting.AnomalyDetector import AnomalyDetector
from autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel import ForecastingModel
from autoai_ts_libs.deps.tspy.data_structures.forecasting.UpdatableAnomalyDetector import UpdatableAnomalyDetector
from autoai_ts_libs.deps.tspy.functions import _online_forecasting_interpolators as interpolators


def load(path):
    tsc = _get_context()
    j_fm = tsc.packages.time_series.transforms.forecastors.PythonConnector.readForecastingModel(path)
    return ForecastingModel(tsc, None, j_fm)


def bats(training_sample_size, box_cox_transform=False):
    """
    Build a BATS model

    Parameters
    ----------
    training_sample_size: int

    box_cox_transform: bool, optional

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    tsc = _get_context()
    bats_algorithm = tsc.packages.time_series.forecasting.algorithms.BATS.BATSAlgorithm(
        training_sample_size,
        box_cox_transform
    )
    return ForecastingModel(tsc, bats_algorithm)

# todo not handling initialization_version yet
def _build_hws(is_multiplicative, error_history_length, use_full_error_history, num_held_out, season_selector,
               samples_per_season, initial_training_seasons, initial_training_samples, initialization_version,
               force_initialization, is_damp):
    tsc = _get_context()
    hws_algorithm_builder = tsc.packages.time_series.forecasting.algorithms.HW.HWSAlgorithmBuilder()

    hws_algorithm_builder \
        .setErrorHorizonLength(error_history_length) \
        .setUseFullErrorHistory(use_full_error_history) \
        .setNumHeldOut(num_held_out)

    if season_selector is not None:
        hws_algorithm_builder.setSeasonSelector(season_selector)
        hws_algorithm_builder.setMaxSamplesPerSeason(samples_per_season)
    else:
        hws_algorithm_builder.setSamplesPerSeason(samples_per_season)

    hws_algorithm_builder \
        .setMultiplicative(is_multiplicative) \
        .setTrainingSeasonCount(initial_training_seasons) \
        .setTrainingSampleCount(initial_training_samples) \
        .setForcedInitialization(force_initialization) \
        .setDamped(is_damp)

    return hws_algorithm_builder.build()

def hws(**kwargs):
    """
    Build a Holt-Winters model

    Parameters
    ----------
    sample_per_season: int

    initial_training_season:

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    tsc = _get_context()
    algorithm_type = kwargs.get("algorithm_type", "additive")
    is_multiplicative = algorithm_type == "multiplicative"
    is_damp = kwargs.get("damp", False)
    num_held_out = 0
    force_initialization = True

    if 'samples_per_season' in kwargs and 'initial_training_seasons' in kwargs:
        samples_per_season = kwargs["samples_per_season"]
        initial_training_seasons = kwargs["initial_training_seasons"]
        initial_training_samples = 0
        error_history_length = kwargs.get("error_history_length", 1)
        use_full_error_history = kwargs.get("use_full_error_history", True)
        compute_seasonality = kwargs.get("compute_seasonality", samples_per_season <= 0)

        if compute_seasonality or samples_per_season < 0:
            _season_selector = season_selector()._j_season_selector
        else:
            _season_selector = None
    elif "is_season_length" in kwargs and "number_of_samples" in kwargs:
        error_history_length = 1
        use_full_error_history = True
        is_season_length = kwargs["is_season_length"]
        number_of_samples = kwargs["number_of_samples"]
        if is_season_length:
            _season_selector = None
            samples_per_season = number_of_samples
            initial_training_seasons = 2
            initial_training_samples = 0
        else:
            _season_selector = season_selector()._j_season_selector
            samples_per_season = 0
            initial_training_seasons = 0
            initial_training_samples = number_of_samples
    else:
        raise ValueError(
            "must have samples_per_seasons/initial_training_seasons or is_season_length/number_of_samples set")

    algorithm = _build_hws(is_multiplicative, error_history_length, use_full_error_history, num_held_out,
                           _season_selector, samples_per_season, initial_training_seasons,
                           initial_training_samples, None, force_initialization, is_damp)
    return ForecastingModel(tsc, algorithm)



def arima(error_horizon_length=1, use_full_error_history=True, force_model=False, min_training_data=-1, p_min=0,
          p_max=-1, d=-1, q_min=0, q_max=-1):
    """
    Build a ARIMA model

    Parameters
    ----------
    error_horizon_length: int, optional (1)

    use_full_error_history: bool, optional (True)
    force_model: bool, optional (False)

    min_training_data: int, optional (1)

    p_min: int, optional (0)
    p_max: int, optional (-1)
    d: int, optional (-1)
    q_min: int, optional (0)
    q_max: int, optional (-1)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    tsc = _get_context()
    arima_algorithm = tsc.packages.time_series.forecasting.algorithms.arima.RegularARIMAAlgorithm(
        error_horizon_length,
        use_full_error_history,
        force_model,
        min_training_data,
        p_min,
        p_max,
        d,
        q_min,
        q_max
    )
    return ForecastingModel(tsc, arima_algorithm)


def arma(min_training_data=-1, p_min=0, p_max=5, q_min=0, q_max=5):
    """
    Build a ARMA model

    Parameters
    ----------
    min_training_data: int, optional (1)

    p_min: int, optional (0)
    p_max: int, optional (5)
    q_min: int, optional (0)
    q_max: int, optional (5)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    tsc = _get_context()
    arma_algorithm = tsc.packages.time_series.forecasting.algorithms.arima.RegularARMAAlgorithm(
        min_training_data,
        p_min,
        p_max,
        q_min,
        q_max
    )
    return ForecastingModel(tsc, arma_algorithm)


def auto(min_training_data, error_history_length=1):
    """
    Build a AUTO model

    Parameters
    ----------
    min_training_data: int

    error_history_length: int, optional (1)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    tsc = _get_context()
    auto_algorithm = tsc.packages.time_series.forecasting.algorithms.selecting.RegularDynamicSelectionAlgorithm(
        error_history_length,
        min_training_data
    )
    return ForecastingModel(tsc, auto_algorithm)


def anomaly_detector(confidence):
    """
    Build a AnomalyDetector model

    Parameters
    ----------
    confidence: float

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.AnomalyDetector.AnomalyDetector`

    """
    tsc = _get_context()
    return AnomalyDetector(tsc, confidence)


def updatable_anomaly_detector(model, confidence, update_anomalies=True):
    """
    Build a AnomalyDetector model

    Parameters
    ----------
    model: :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`
        the anomaly detectors forecasting model

    confidence: float
        used in computation of confidence interval

    update_anomalies: boolean, optional
        if True, will update the model with an anomaly if found, otherwise anomalies will not be trained into the model
        (default is True)
    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.UpdatableAnomalyDetector.UpdatableAnomalyDetector`
        an updatable anomaly detector
    """
    tsc = _get_context()
    j_anomaly_detector = tsc.packages.time_series.forecasting.anomaly.pointwise \
        .BoundedAnomalyDetector(model._j_fm, confidence, update_anomalies)
    return UpdatableAnomalyDetector(tsc, j_anomaly_detector)


def windowed_knn_anomaly_detector(confidence, k, min_windows, regular_interval, window_size, history_length,
                                  interpolator=None):
    tsc = _get_context()
    j_anomaly_detector = tsc.packages.time_series.forecasting.anomaly.windowed \
        .WindowedKNNAnomalyDetector(confidence, k, min_windows, regular_interval, window_size, history_length,
                                    interpolator)
    return UpdatableAnomalyDetector(tsc, j_anomaly_detector)


def windowed_residual_anomaly_detector(regular_interval, window_size, interpolator, model, anomaly_detector):
    tsc = _get_context()
    j_anomaly_detector = tsc.packages.time_series.forecasting.anomaly.windowed \
        .WindowedResidualAnomalyDetector(regular_interval, window_size, interpolator, model._j_fm,
                                         anomaly_detector._j_anomaly_detector)
    return UpdatableAnomalyDetector(tsc, j_anomaly_detector)


def season_selector(sub_season_percent_delta=0.0, max_season_length=None):
    """
    Build a SeasonSelector model

    Parameters
    ----------
    sub_season_percent_delta: float, optional (0.0)
    max_season_length: int, optional (None)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.SeasonSelector.SeasonSelector`

    """
    tsc = _get_context()
    j_season_selector = tsc.packages.time_series.forecasting.util.RegularFFTSeasonSelector(
        sub_season_percent_delta, 0 if max_season_length is None else max_season_length)
    from autoai_ts_libs.deps.tspy.data_structures.forecasting.SeasonSelector import SeasonSelector
    return SeasonSelector(tsc, j_season_selector)

def var(history_length=1):
    tsc = _get_context()
    vector_autoregression = tsc.packages.time_series.transforms.forecastors.Forecasters.var(history_length)
    return vector_autoregression

def arimax(difference_all_data=True, disable_difference=False, diff_eta=True):
    tsc = _get_context()
    if disable_difference:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXAlgorithm(
            disable_difference
        )
    else:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXAlgorithm(
            difference_all_data, diff_eta
        )
    from autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingAlgorithm import ForecastingAlgorithm
    return ForecastingAlgorithm(tsc, arimax_algorithm)


def arimax_palr(difference_all_data=True, disable_difference=False, diff_eta=True):
    tsc = _get_context()
    if disable_difference:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXPALRAlgorithm(
            disable_difference
        )
    else:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXPALRAlgorithm(
            difference_all_data, diff_eta
        )
    from autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingAlgorithm import ForecastingAlgorithm
    return ForecastingAlgorithm(tsc, arimax_algorithm)


def arimax_rar(difference_all_data=True, disable_difference=False, diff_eta=True):
    tsc = _get_context()
    if disable_difference:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXRARAlgorithm(
            disable_difference
        )
    else:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXRARAlgorithm(
            difference_all_data, diff_eta
        )
    from autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingAlgorithm import ForecastingAlgorithm
    return ForecastingAlgorithm(tsc, arimax_algorithm)

def arimax_rsar(difference_all_data=True, disable_difference=False, diff_eta=True):
    tsc = _get_context()
    if disable_difference:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXRSARAlgorithm(
            disable_difference
        )
    else:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.ARIMAXRSARAlgorithm(
            difference_all_data, diff_eta
        )
    from autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingAlgorithm import ForecastingAlgorithm
    return ForecastingAlgorithm(tsc, arimax_algorithm)

def arimax_dmlr(difference_all_data=True, disable_difference=False, diff_eta=True):
    tsc = _get_context()
    if disable_difference:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.DMLRAlgorithm(
            disable_difference
        )
    else:
        arimax_algorithm = tsc.packages.time_series.forecasting.algorithms.arimax.DMLRAlgorithm(
            difference_all_data, diff_eta
        )
    from autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingAlgorithm import ForecastingAlgorithm
    return ForecastingAlgorithm(tsc, arimax_algorithm)
