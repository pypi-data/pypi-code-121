#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.

from datarobot.enums import MONOTONICITY_FEATURELIST_DEFAULT
from datarobot.models import DatetimeModel as datarobot_datetime_model
from datarobot.models import Model as datarobot_model
from datarobot.utils import get_id_from_response


class Model(datarobot_model):
    def train_datetime(
        self,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        time_window_sample_pct=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        use_project_settings=False,
        sampling_method=None,
        n_clusters=None,
    ):
        """Trains this model on a different featurelist or sample size.

        Requires that this model is part of a datetime partitioned project; otherwise, an error will
        occur.

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        featurelist_id : str, optional
            the featurelist to use to train the model.  If not specified, the featurelist of this
            model is used.
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            neither ``training_duration`` nor ``use_project_settings`` may be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, neither ``training_row_count`` nor ``use_project_settings`` may be
            specified.
        use_project_settings : bool, optional
            (New in version v2.20) defaults to ``False``. If ``True``, indicates that the custom
            backtest partitioning settings specified by the user will be used to train the model and
            evaluate backtest scores. If specified, neither ``training_row_count`` nor
            ``training_duration`` may be specified.
        time_window_sample_pct : int, optional
            may only be specified when the requested model is a time window (e.g. duration or start
            and end dates). An integer between 1 and 99 indicating the percentage to sample by
            within the window. The points kept are determined by a random uniform sample.
            If specified, training_duration must be specified otherwise, the number of rows used
            to train the model and evaluate backtest scores and an error will occur.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.
        monotonic_increasing_featurelist_id : str, optional
            (New in version v2.18) optional, the id of the featurelist that defines
            the set of features with a monotonically increasing relationship to the target.
            Passing ``None`` disables increasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        monotonic_decreasing_featurelist_id : str, optional
            (New in version v2.18) optional, the id of the featurelist that defines
            the set of features with a monotonically decreasing relationship to the target.
            Passing ``None`` disables decreasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        n_clusters: int, optional
            (new in version 2.27) Number of clusters to use in an unsupervised clustering model.
            This parameter is used only for unsupervised clustering models that don't automatically
            determine the number of clusters.

        Returns
        -------
        job : ModelJob
            the created job to build the model
        """
        # TODO: revert this import to 'from .modeljob import ModelJob" when moving to master.
        from datarobot.models.modeljob import ModelJob

        url = "projects/{}/datetimeModels/".format(self.project_id)
        flist_id = featurelist_id or self.featurelist_id
        payload = {"blueprint_id": self.blueprint_id, "featurelist_id": flist_id}
        if training_row_count:
            payload["training_row_count"] = training_row_count
        if training_duration:
            payload["training_duration"] = training_duration
        if time_window_sample_pct:
            payload["time_window_sample_pct"] = time_window_sample_pct
        if sampling_method:
            payload["sampling_method"] = sampling_method
        if monotonic_increasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_increasing_featurelist_id"] = monotonic_increasing_featurelist_id
        if monotonic_decreasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_decreasing_featurelist_id"] = monotonic_decreasing_featurelist_id
        if use_project_settings:
            payload["use_project_settings"] = use_project_settings
        if n_clusters:
            payload["n_clusters"] = n_clusters
        response = self._client.post(
            url,
            data=payload,
            keep_attrs=[
                "monotonic_increasing_featurelist_id",
                "monotonic_decreasing_featurelist_id",
            ],
        )
        return ModelJob.from_id(self.project_id, get_id_from_response(response))


class DatetimeModel(datarobot_datetime_model):
    """Represents a model from a datetime partitioned project

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Note that only one of `training_row_count`, `training_duration`, and
    `training_start_date` and `training_end_date` will be specified, depending on the
    `data_selection_method` of the model.  Whichever method was selected determines the amount of
    data used to train on when making predictions and scoring the backtests and the holdout.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    training_row_count : int or None
        If specified, an int specifying the number of rows used to train the model and evaluate
        backtest scores.
    training_duration : str or None
        If specified, a duration string specifying the duration spanned by the data used to train
        the model and evaluate backtest scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    time_window_sample_pct : int or None
        An integer between 1 and 99 indicating the percentage of sampling within the training
        window.  The points kept are determined by a random uniform sample.  If not specified, no
        sampling was done.
    sampling_method : str or None
        (New in v2.23) indicates the way training data has been selected (either how rows have been
        selected within backtest or how ``time_window_sample_pct`` has been applied).
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric.  The keys in metrics are
        the different metrics used to evaluate the model, and the values are the results.  The
        dictionaries inside of metrics will be as described here: 'validation', the score
        for a single backtest; 'crossValidation', always None; 'backtesting', the average score for
        all backtests if all are available and computed, or None otherwise; 'backtestingScores', a
        list of scores for all backtests where the score is None if that backtest does not have a
        score available; and 'holdout', the score for the holdout or None if the holdout is locked
        or the score is unavailable.
    backtests : list of dict
        describes what data was used to fit each backtest, the score for the project metric, and
        why the backtest score is unavailable if it is not provided.
    data_selection_method : str
        which of training_row_count, training_duration, or training_start_data and training_end_date
        were used to determine the data used to fit the model.  One of 'rowCount',
        'duration', or 'selectedDateRange'.
    training_info : dict
        describes which data was used to train on when scoring the holdout and making predictions.
        training_info` will have the following keys: `holdout_training_start_date`,
        `holdout_training_duration`, `holdout_training_row_count`, `holdout_training_end_date`,
        `prediction_training_start_date`, `prediction_training_duration`,
        `prediction_training_row_count`, `prediction_training_end_date`. Start and end dates will
        be datetimes, durations will be duration strings, and rows will be integers.
    holdout_score : float or None
        the score against the holdout, if available and the holdout is unlocked, according to the
        project metric.
    holdout_status : string or None
        the status of the holdout score, e.g. "COMPLETED", "HOLDOUT_BOUNDARIES_EXCEEDED".
        Unavailable if the holdout fold was disabled in the partitioning configuration.
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    supports_monotonic_constraints : bool
        optional, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    effective_feature_derivation_window_start : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the past relative to the forecast point
        the user needs to provide history for at prediction time. This can differ from the
        ``feature_derivation_window_start`` set on the project due to the differencing method and
        period selected, or if the model is a time series native model such as ARIMA. Will be a
        negative integer in time series projects and ``None`` otherwise.
    effective_feature_derivation_window_end : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the past relative to the forecast point
        the feature derivation window should end. Will be a non-positive integer in time series
        projects and ``None`` otherwise.
    forecast_window_start : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the future relative to the forecast point
        the forecast window should start. Note that this field will be the same as what is shown in
        the project settings. Will be a non-negative integer in time series projects and `None`
        otherwise.
    forecast_window_end : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the future relative to the forecast point
        the forecast window should end. Note that this field will be the same as what is shown in
        the project settings. Will be a non-negative integer in time series projects and `None`
        otherwise.
    windows_basis_unit : str or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        Indicates which unit is the basis for the feature derivation window and the forecast window.
        Note that this field will be the same as what is shown in the project settings. In time
        series projects, will be either the detected time unit or "ROW", and `None` otherwise.
    model_number : integer
        model number assigned to a model
    parent_model_id : str or None
        (New in version v2.20) the id of the model that tuning parameters are derived from
    use_project_settings : bool or None
        (New in version v2.20) If ``True``, indicates that the custom backtest partitioning settings
        specified by the user were used to train the model and evaluate backtest scores.
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    is_n_clusters_dynamically_determined : bool
        (new in version 2.27) if ``True``, indicates that model determines number of clusters
        automatically
    n_clusters : int
        (new in version 2.27) Number of clusters to use in an unsupervised clustering model.
        This parameter is used only for unsupervised clustering models that don't automatically
        determine the number of clusters.
    """

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        time_window_sample_pct=None,
        sampling_method=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        blueprint_id=None,
        metrics=None,
        training_info=None,
        holdout_score=None,
        holdout_status=None,
        data_selection_method=None,
        backtests=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        effective_feature_derivation_window_start=None,
        effective_feature_derivation_window_end=None,
        forecast_window_start=None,
        forecast_window_end=None,
        windows_basis_unit=None,
        model_number=None,
        parent_model_id=None,
        use_project_settings=None,
        supports_composable_ml=None,
        n_clusters=None,
        is_n_clusters_dynamically_determined=None,
    ):
        super(DatetimeModel, self).__init__(
            id=id,
            processes=processes,
            featurelist_name=featurelist_name,
            featurelist_id=featurelist_id,
            project_id=project_id,
            sample_pct=sample_pct,
            training_row_count=training_row_count,
            training_duration=training_duration,
            training_start_date=training_start_date,
            training_end_date=training_end_date,
            model_type=model_type,
            model_category=model_category,
            is_frozen=is_frozen,
            blueprint_id=blueprint_id,
            metrics=metrics,
            monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
            supports_monotonic_constraints=supports_monotonic_constraints,
            is_starred=is_starred,
            prediction_threshold=prediction_threshold,
            prediction_threshold_read_only=prediction_threshold_read_only,
            model_number=model_number,
            parent_model_id=parent_model_id,
            use_project_settings=use_project_settings,
            supports_composable_ml=supports_composable_ml,
        )
        # TODO: upon move to master, these should be added to `super` call (initialized
        # via original `Model.__init__`).
        self.n_clusters = n_clusters
        self.is_n_clusters_dynamically_determined = is_n_clusters_dynamically_determined

    def retrain(
        self,
        time_window_sample_pct=None,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        sampling_method=None,
        n_clusters=None,
    ):
        """Retrain an existing datetime model using a new training period for the model's training
        set (with optional time window sampling) or a different feature list.

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        featurelist_id : str, optional
            The ID of the featurelist to use.
        training_row_count : str, optional
            The number of rows to train the model on. If this parameter is used then `sample_pct`
            cannot be specified.
        time_window_sample_pct : int, optional
            An int between ``1`` and ``99`` indicating the percentage of
            sampling within the time window. The points kept are determined by a random uniform
            sample. If specified, `training_row_count` must not be specified and either
            `training_duration` or `training_start_date` and `training_end_date` must be specified.
        training_duration : str, optional
            A duration string representing the training duration for the submitted model. If
            specified then `training_row_count`, `training_start_date`, and `training_end_date`
            cannot be specified.
        training_start_date : str, optional
            A datetime string representing the start date of
            the data to use for training this model.  If specified, `training_end_date` must also be
            specified, and `training_duration` cannot be specified. The value must be before the
            `training_end_date` value.
        training_end_date : str, optional
            A datetime string representing the end date of the
            data to use for training this model.  If specified, `training_start_date` must also be
            specified, and `training_duration` cannot be specified. The value must be after the
            `training_start_date` value.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.
        n_clusters : int, optional
            (new in version 2.27) Number of clusters to use in an unsupervised clustering model.
            This parameter is used only for unsupervised clustering models that don't automatically
            determine the number of clusters.

        Returns
        -------
        job : ModelJob
            The created job that is retraining the model
        """
        if bool(training_start_date) ^ bool(training_end_date):
            raise ValueError("Both training_start_date and training_end_date must be specified.")
        if training_duration and training_row_count:
            raise ValueError(
                "Only one of training_duration or training_row_count should be specified."
            )
        if time_window_sample_pct and not training_duration and not training_start_date:
            raise ValueError(
                "time_window_sample_pct should only be used with either "
                "training_duration or training_start_date and training_end_date"
            )
        # TODO: revert this import to 'from .modeljob import ModelJob" when moving to master.
        from datarobot.models.modeljob import ModelJob

        url = "projects/{}/datetimeModels/fromModel/".format(self.project_id)
        payload = {
            "modelId": self.id,
            "featurelistId": featurelist_id,
            "timeWindowSamplePct": time_window_sample_pct,
            "trainingRowCount": training_row_count,
            "trainingDuration": training_duration,
            "trainingStartDate": training_start_date,
            "trainingEndDate": training_end_date,
        }
        if sampling_method:
            payload["samplingMethod"] = sampling_method
        if n_clusters:
            payload["nClusters"] = n_clusters
        response = self._client.post(url, data=payload)
        return ModelJob.from_id(self.project_id, get_id_from_response(response))
