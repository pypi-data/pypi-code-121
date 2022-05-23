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
from datarobot.models import ModelJob
from datarobot.models import Project as datarobot_project
from datarobot.utils import get_id_from_response
from datarobot.utils.pagination import unpaginate


class Project(datarobot_project):
    """
    Please see datarobot.Project for primary documentation.

    The experimental version of project adds the following functionality:
    - Specify number of clusters when training TS clustering model.
    """

    def train_datetime(
        self,
        blueprint_id,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        source_project_id=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        use_project_settings=False,
        sampling_method=None,
        n_clusters=None,
    ):
        """Create a new model in a datetime partitioned project

        If the project is not datetime partitioned, an error will occur.

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        blueprint_id : str
            the blueprint to use to train the model
        featurelist_id : str, optional
            the featurelist to use to train the model.  If not specified, the project default will
            be used.
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            neither ``training_duration`` nor ``use_project_settings`` may be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, neither ``training_row_count`` nor ``use_project_settings`` may be
            specified.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.
        use_project_settings : bool, optional
            (New in version v2.20) defaults to ``False``. If ``True``, indicates that the custom
            backtest partitioning settings specified by the user will be used to train the model and
            evaluate backtest scores. If specified, neither ``training_row_count`` nor
            ``training_duration`` may be specified.
        source_project_id : str, optional
            the id of the project this blueprint comes from, if not this project.  If left
            unspecified, the blueprint must belong to this project.
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
        n_clusters : int, optional
            optional, The number of clusters to use in the specified unsupervised clustering model.
            ONLY VALID IN UNSUPERVISED CLUSTERING PROJECTS

        Returns
        -------
        job : ModelJob
            the created job to build the model
        """
        url = "{}{}/datetimeModels/".format(self._path, self.id)
        payload = {"blueprint_id": blueprint_id}
        if featurelist_id is not None:
            payload["featurelist_id"] = featurelist_id
        if source_project_id is not None:
            payload["source_project_id"] = source_project_id
        if training_row_count is not None:
            payload["training_row_count"] = training_row_count
        if training_duration is not None:
            payload["training_duration"] = training_duration
        if sampling_method is not None:
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
        job_id = get_id_from_response(response)
        return ModelJob.from_id(self.id, job_id)

    # TODO: skip when merging back to master. It's all about inline Model import inside.
    def get_models(self, order_by=None, search_params=None, with_metric=None):
        """
        List all completed, successful models in the leaderboard for the given project.

        Parameters
        ----------
        order_by : str or list of strings, optional
            If not `None`, the returned models are ordered by this
            attribute. If `None`, the default return is the order of
            default project metric.

            Allowed attributes to sort by are:

            * ``metric``
            * ``sample_pct``

            If the sort attribute is preceded by a hyphen, models will be sorted in descending
            order, otherwise in ascending order.

            Multiple sort attributes can be included as a comma-delimited string or in a list
            e.g. order_by=`sample_pct,-metric` or order_by=[`sample_pct`, `-metric`]

            Using `metric` to sort by will result in models being sorted according to their
            validation score by how well they did according to the project metric.
        search_params : dict, optional.
            If not `None`, the returned models are filtered by lookup.
            Currently you can query models by:

            * ``name``
            * ``sample_pct``
            * ``is_starred``

        with_metric : str, optional.
            If not `None`, the returned models will only have scores for this
            metric. Otherwise all the metrics are returned.

        Returns
        -------
        models : a list of Model instances.
            All of the models that have been trained in this project.

        Raises
        ------
        TypeError
            Raised if ``order_by`` or ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------

        .. code-block:: python

            Project.get('pid').get_models(order_by=['-sample_pct',
                                          'metric'])

            # Getting models that contain "Ridge" in name
            # and with sample_pct more than 64
            Project.get('pid').get_models(
                search_params={
                    'sample_pct__gt': 64,
                    'name': "Ridge"
                })

            # Filtering models based on 'starred' flag:
            Project.get('pid').get_models(search_params={'is_starred': True})
        """
        from datarobot._experimental import Model

        url = "{}{}/models/".format(self._path, self.id)
        get_params = {}
        if order_by is not None:
            order_by = self._canonize_order_by(order_by)
            get_params.update({"order_by": order_by})
        else:
            get_params.update({"order_by": "-metric"})
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError("Provided search_params argument is invalid")
        if with_metric is not None:
            get_params.update({"with_metric": with_metric})
        if "is_starred" in get_params:
            get_params["is_starred"] = "true" if get_params["is_starred"] else "false"
        resp_data = self._client.get(url, params=get_params).json()
        init_data = [dict(Model._safe_data(item), project=self) for item in resp_data]
        return [Model(**data) for data in init_data]

    # TODO: skip when merging back to master. It's all about inline DatetimeModel import inside.
    def get_datetime_models(self):
        """List all models in the project as DatetimeModels

        Requires the project to be datetime partitioned.  If it is not, a ClientError will occur.

        Returns
        -------
        models : list of DatetimeModel
            the datetime models
        """
        from datarobot._experimental import DatetimeModel

        url = "{}{}/datetimeModels/".format(self._path, self.id)
        data = unpaginate(url, None, self._client)
        return [DatetimeModel.from_server_data(item) for item in data]
