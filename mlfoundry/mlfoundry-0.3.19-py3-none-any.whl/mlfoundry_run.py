import atexit
import datetime
import json
import logging
import os
import queue
import time
import weakref
from typing import Any, Collection, Dict, Iterable, List, Optional, Union

import mlflow
import numpy as np
import pandas as pd
import whylogs
from mlflow.entities import Metric, Param, RunStatus, RunTag
from mlflow.tracking import MlflowClient

from mlfoundry import amplitude, constants, enums
from mlfoundry.background.interface import Interface
from mlfoundry.background.sender import SenderJob
from mlfoundry.background.system_metrics import SystemMetricsJob
from mlfoundry.dataset import DataSet, TabularDatasetDriver
from mlfoundry.exceptions import MlflowException, MlFoundryException
from mlfoundry.git_info import GitInfo
from mlfoundry.internal_namespace import NAMESPACE
from mlfoundry.metrics.v1 import get_metrics_calculator as get_metrics_calculator_v1
from mlfoundry.metrics.v2 import ComputedMetrics
from mlfoundry.metrics.v2 import get_metrics_calculator as get_metrics_calculator_v2
from mlfoundry.model import ModelDriver
from mlfoundry.run_utils import (
    NumpyEncoder,
    ParamsType,
    log_artifact_blob,
    process_params,
)
from mlfoundry.schema import Schema

logger = logging.getLogger(__name__)


class MlFoundryRun:
    """MlFoundryRun."""

    # TODO (nikunjbjj): Seems like these artifact locations are defined in constants.py for loading.
    #  Need to change this.
    S3_DATASET_PATH = "datasets"
    S3_STATS_PATH = "stats"
    S3_WHYLOGS_PATH = "whylogs"
    S3_METRICS_PATH = "multi_dimensional_metrics"

    def __init__(
        self,
        experiment_id: str,
        run_id: str,
        log_system_metrics: bool = False,
        **kwargs,
    ):
        """__init__.

        Args:
            experiment_id (str): experiment_id
            run_id (str): run_id
            log_system_metrics (bool): log_system_metrics
        """
        # TODO (chiragjn): rename experiment to project everywhere
        self._experiment_id = str(experiment_id)
        self._project_name = mlflow.get_experiment(self._experiment_id).name
        # TODO (chiragjn): mlflow_client be a protected/private member
        self.mlflow_client = MlflowClient()
        self._run_id = run_id
        self._dataset_module: TabularDatasetDriver = TabularDatasetDriver(
            mlflow_client=self.mlflow_client, run_id=run_id
        )
        self._model_driver: ModelDriver = ModelDriver(
            mlflow_client=self.mlflow_client, run_id=run_id
        )
        # TODO (chiragjn): Make a settings module and allow enabling/disabling collection and changing intervals
        if log_system_metrics:
            # Interface and Sender do not belong under this condition but for now we don't need to init them otherwise
            self._interface = Interface(
                run_id=self.run_id,
                event_queue=queue.Queue(),
            )
            self._sender_job = SenderJob(
                interface=self._interface,
                mlflow_client=self.mlflow_client,
                interval=0.0,
            )
            self._system_metrics_job = SystemMetricsJob(
                pid=os.getpid(),
                interface=self._interface,
                num_samples_to_aggregate=15,
                interval=2.0,
            )
        else:
            self._interface = None
            self._sender_job = None
            self._system_metrics_job = None
        self._terminate_called = False
        self._start()

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def run_name(self) -> str:
        # TODO (chiragjn): cache this
        return self.mlflow_client.get_run(self.run_id).info.name

    @property
    def project_name(self) -> str:
        return self._project_name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} at 0x{id(self):x}: run_id={self.run_id!r}>"

    def __enter__(self):
        return self

    def _stop_background_jobs(self):
        """Stop launched background jobs for a `run`.

        Stop launched background jobs (system metrics, sender) if any and
        try to finish them gracefully.
        """
        # expect that this function can be called more than once in non-ideal scenarios and defend for it
        if not any([self._interface, self._system_metrics_job, self._sender_job]):
            return

        logger.info(
            f"Shutting down background jobs and syncing data for run with id {self.run_id!r}, "
            f"please don't kill this process..."
        )
        # Stop event producers
        if self._system_metrics_job:
            self._system_metrics_job.stop(timeout=2)
        # Stop accepting more events
        if self._interface:
            self._interface.close()
        # Finish consuming whatever is left
        if self._sender_job:
            try:
                self._sender_job.stop(disable_sleep=True, timeout=10)
            except KeyboardInterrupt:
                # TODO (chiragjn): Separate internal logging and stream to show messages to user
                print(
                    "Ctrl-C interrupt detected, background jobs are still terminating. "
                    "Press Ctrl-C again to stop."
                )
                self._sender_job.stop(disable_sleep=True, timeout=10)
        self._system_metrics_job = None
        self._sender_job = None
        self._interface = None

        logger.info(
            f"Finished syncing data for run with id {self.run_id!r}. Thank you for waiting!"
        )

    def _terminate_run_if_running(self, termination_status: RunStatus):
        """_terminate_run_if_running.

        Args:
            termination_status (RunStatus): termination_status
        """
        if self._terminate_called:
            return

        # Prevent double execution for termination
        self._terminate_called = True

        current_status = None
        try:
            # TODO (chiragjn): This is a network call, should we just cache it on the instance?
            current_status = self.mlflow_client.get_run(self.run_id).info.status
        except Exception as e:
            logger.warning(f"failed to get run status {termination_status} due to {e}")

        try:
            self._stop_background_jobs()
            # we do not need to set any termination status unless the run was in RUNNING state
            if current_status != RunStatus.to_string(RunStatus.RUNNING):
                return
            self.mlflow_client.set_terminated(
                self.run_id, RunStatus.to_string(termination_status)
            )
        except Exception as e:
            logger.warning(
                f"failed to set termination status {termination_status} due to {e}"
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = RunStatus.FINISHED if exc_type is None else RunStatus.FAILED
        self._terminate_run_if_running(status)

    def __del__(self):
        # TODO (chiragjn): Should this be marked as FINISHED or KILLED?
        self._terminate_run_if_running(RunStatus.FINISHED)

    def _start(self):
        def terminate_run_if_running_with_weakref(
            mlf_run_weakref: "weakref.ReferenceType[MlFoundryRun]",
            termination_status: RunStatus,
        ):
            _run = mlf_run_weakref()
            if _run:
                _run._terminate_run_if_running(termination_status)

        atexit.register(
            terminate_run_if_running_with_weakref, weakref.ref(self), RunStatus.FINISHED
        )
        if self._sender_job:
            self._sender_job.start()
        if self._system_metrics_job:
            self._system_metrics_job.start()

    def end(self):
        """End a `run`.

        This function marks the run as `FINISHED`.

        Example:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        )
        # ...
        # Model training code
        # ...
        run.end()
        ```

        In case the run was created using the context manager approach,
        We do not need to call this function.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        with client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        ) as run:
            # ...
            # Model training code
            ...
        # `run` will be automatically marked as `FINISHED` or `FAILED`.
        ```
        """
        self._terminate_run_if_running(RunStatus.FINISHED)

    def _add_git_info(self, root_path: Optional[str] = None):
        """_add_git_info.

        Args:
            root_path (Optional[str]): root_path
        """
        root_path = root_path or os.getcwd()
        try:
            git_info = GitInfo(root_path)
            tags = [
                RunTag(
                    key=constants.GIT_COMMIT_TAG_NAME,
                    value=git_info.current_commit_sha,
                ),
                RunTag(
                    key=constants.GIT_BRANCH_TAG_NAME,
                    value=git_info.current_branch_name,
                ),
                RunTag(key=constants.GIT_DIRTY_TAG_NAME, value=str(git_info.is_dirty)),
            ]
            remote_url = git_info.remote_url
            if remote_url is not None:
                tags.append(RunTag(key=constants.GIT_REMOTE_URL_NAME, value=remote_url))
            self.mlflow_client.log_batch(run_id=self.run_id, tags=tags)
            log_artifact_blob(
                mlflow_client=self.mlflow_client,
                run_id=self.run_id,
                blob=git_info.diff_patch,
                file_name=constants.PATCH_FILE_NAME,
                artifact_path=constants.PATCH_FILE_ARTIFACT_DIR,
            )
        except Exception as ex:
            # no-blocking
            logger.warning(f"failed to log git info because {ex}")

    def download_artifact(self, path: str, dest_path: Optional[str] = None) -> str:
        """Downloads a logged `artifact` associated with the current `run`.

        Args:
            path (str): Source artifact path.
            dest_path (Optional[str], optional): Absolute path of the local destination
                directory. If a directory path is passed, the directory must already exist.
                If not passed, the artifact will be downloaded to a newly created directory
                in the local filesystem.

        Returns:
            str: Path of the directory where the artifact is downloaded.

        Examples:
        ```python
        import os
        import mlfoundry

        with open("artifact.txt", "w") as f:
            f.write("hello-world")

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        )

        run.log_artifact(local_path="artifact.txt", artifact_path="my-artifacts")

        local_path = run.download_artifact(path="my-artifacts")
        print(f"Artifacts: {os.listdir(local_path)}")

        run.end()
        ```
        """
        if dest_path is None:
            return self.mlflow_client.download_artifacts(self.run_id, path=path)
        elif os.path.isdir(dest_path):
            return self.mlflow_client.download_artifacts(
                self.run_id, path=path, dst_path=dest_path
            )
        else:
            raise MlFoundryException(
                f"Destination path {dest_path} should be an existing directory."
            )

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Logs an artifact for the current `run`.

        An `artifact` is a local file or directory. This function stores the `artifact`
        at the remote artifact storage.

        Args:
            local_path (str): Local path of the file or directory.
            artifact_path (Optional[str], optional): Relative destination path where
                the `artifact` will be stored. If not passed, the `artifact` is stored
                at the root path of the `run`'s artifact storage. The passed
                `artifact_path` should not start with `mlf/`, as `mlf/` directory is
                reserved for `mlfoundry`.

        Examples:
        ```python
        import os
        import mlfoundry

        with open("artifact.txt", "w") as f:
            f.write("hello-world")

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        )

        run.log_artifact(local_path="artifact.txt", artifact_path="my-artifacts")

        run.end()
        ```
        """
        logger.info(f"Logging {local_path!r} as artifact, this might take a while ...")
        if artifact_path is not None:
            NAMESPACE.validate_namespace_not_used(path=artifact_path)
        if os.path.isfile(local_path):
            self.mlflow_client.log_artifact(
                self.run_id, local_path=local_path, artifact_path=artifact_path
            )
        elif os.path.isdir(local_path):
            self.mlflow_client.log_artifacts(
                self.run_id, local_dir=local_path, artifact_path=artifact_path
            )
        else:
            raise MlFoundryException(
                f"local path {local_path} should be an existing file or directory"
            )

    def log_dataset(
        self,
        dataset_name: str,
        features,
        predictions=None,
        actuals=None,
        only_stats: bool = False,
    ):
        """Log a tabular dataset for the current `run`.

        Log a dataset associated with a run. A dataset is a collection of features,
        predictions and actuals. Datasets are uniquely identified by the `dataset_name`
        under a run. They are immutable, once successfully logged, overwriting it is not allowed.
        Mixed types are not allowed in features, actuals and predictions. However, there can be
        missing data in the form of None, NaN, NA.

        The statistics can be visualized in the mlfoundry dashboard.

        Args:
            dataset_name (str): Name of the dataset. Dataset name should only contain
                letters(a-b, A-B), numbers (0-9), underscores (_) and hyphens (-).
            features: Features associated with this dataset.
                This should be either pandas DataFrame or should be of a
                data type which can be converted to a DataFrame.
            predictions (Iterable,optional): Predictions associated with this dataset and run. This
                should be either pandas Series or should be of a data type which
                can be converted to a Series. This is an optional argument.
            actuals (Iterable, optional): Actuals associated with this dataset and run. This
                should be either pandas Series or should be of a data type which
                can be converted to a Series. This is an optional argument.
            only_stats (bool, optional): If True, then the dataset
                (features, predictions, actuals) is not saved. Only statistics and
                the dataset schema will be persisted. Default is False.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        )

        features = [
            {"feature_1": 1, "feature_2": 1.2, "feature_3": "high"},
            {"feature_1": 2, "feature_2": 3.5, "feature_3": "medium"},
        ]
        run.log_dataset(
            dataset_name="train",
            features=features,
            actuals=[1.2, 1.3],
            predictions=[3.1, 4.5],
        )

        run.end()
        ```
        """
        amplitude.track(amplitude.Event.LOG_DATASET)
        logger.info("Logging Dataset, this might take a while ...")
        self._dataset_module.log_dataset(
            dataset_name=dataset_name,
            features=features,
            predictions=predictions,
            actuals=actuals,
            only_stats=only_stats,
        )
        logger.info("Dataset logged successfully")

    def get_dataset(self, dataset_name: str) -> Optional[DataSet]:
        """Get a logged dataset by `dataset_name`.

        Args:
            dataset_name (str): Name of the dataset.

        Returns:
            Optional[DataSet]: Returns logged dataset as an instance of
                the `DataSet` class. If the dataset was not logged or
                `only_stats` was set to `True` while logging the dataset,
                the function will return `None`.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        )

        features = [
            {"feature_1": 1, "feature_2": 1.2, "feature_3": "high"},
            {"feature_1": 2, "feature_2": 3.5, "feature_3": "medium"},
        ]
        run.log_dataset(
            dataset_name="train",
            features=features,
            actuals=[1.2, 1.3],
            predictions=[3.1, 4.5],
        )
        dataset = run.get_dataset("train")
        print(dataset.features) # This will be in Pandas DataFrame type.
        print(dataset.predictions) # This will be in Pandas Series type.
        print(dataset.actuals) # This will be in Pandas Series type.
        run.end()
        ```
        """
        amplitude.track(amplitude.Event.LOG_DATASET)
        return self._dataset_module.get_dataset(dataset_name=dataset_name)

    def log_metrics(self, metric_dict: Dict[str, Union[int, float]], step: int = 0):
        """Log metrics for the current `run`.

        A metric is defined by a metric name (such as "training-loss") and a
        floating point or integral value (such as `1.2`). A metric is associated
        with a `step` which is the training iteration at which the metric was
        calculated.

        Args:
            metric_dict (Dict[str, Union[int, float]]): A metric name to metric value map.
                metric value should be either `float` or `int`. This should be
                a non-empty dictionary.
            step (int, optional): Training step/iteration at which the metrics
                present in `metric_dict` were calculated. If not passed, `0` is
                set as the `step`.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project"
        )
        run.log_metrics(metric_dict={"accuracy": 0.7, "loss": 0.6}, step=0)
        run.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4}, step=1)

        run.end()
        ```
        """
        # not sure about amplitude tracking here.
        # as the user can use this function in training loop
        # amplitude.track(amplitude.Event.LOG_METRICS)

        try:
            # mlfow_client doesn't have log_metrics api, so we have to use log_batch,
            # This is what internally used by mlflow.log_metrics
            timestamp = int(time.time() * 1000)
            metrics_arr = [
                Metric(key, value, timestamp, step=step)
                for key, value in metric_dict.items()
            ]
            if len(metrics_arr) == 0:
                raise MlflowException("Cannot log empty metrics dictionary")

            self.mlflow_client.log_batch(
                run_id=self.run_id, metrics=metrics_arr, params=[], tags=[]
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None

        logger.info("Metrics logged successfully")

    def log_params(self, param_dict: ParamsType):
        """Logs parameters for the run.

        Parameters or Hyperparameters can be thought of as configurations for a run.
        For example, the type of kernel used in a SVM model is a parameter.
        A Parameter is defined by a name and a string value. Parameters are
        also immutable, we cannot overwrite parameter value for a parameter
        name.

        Args:
            param_dict (ParamsType): A parameter name to parameter value map.
                Parameter values are converted to `str`.

        Examples:
        ### Logging parameters using a `dict`.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project"
        )
        run.log_params({"learning_rate": 0.01, "epochs": 10})

        run.end()
        ```

        ### Logging parameters using `argparse` Namespace object
        ```python
        import argparse
        import mlfoundry

        parser = argparse.ArgumentParser()
        parser.add_argument("-batch_size", type=int, required=True)
        args = parser.parse_args()

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project"
        )
        run.log_params(args)
        ```
        """
        amplitude.track(amplitude.Event.LOG_PARAMS)

        try:
            # mlfowclient doesnt have log_params api, so we have to use log_batch,
            # This is what internally used by mlflow.log_params
            param_dict = process_params(param_dict)
            params_arr = [Param(key, str(value)) for key, value in param_dict.items()]

            if len(params_arr) == 0:
                raise MlflowException("Cannot log empty params dictionary")

            self.mlflow_client.log_batch(
                run_id=self.run_id, metrics=[], params=params_arr, tags=[]
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None
        logger.info("Parameters logged successfully")

    def set_tags(self, tags: Dict[str, str]):
        """Set tags for the current `run`.

        Tags are "labels" for a run. A tag is represented by a tag name and value.

        Args:
            tags (Dict[str, str]): A tag name to value map.
                Tag name cannot start with `mlf.`, `mlf.` prefix
                is reserved for mlfoundry. Tag values will be converted
                to `str`.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project"
        )
        run.set_tags({"nlp.framework": "Spark NLP"})

        run.end()
        ```
        """
        amplitude.track(amplitude.Event.SET_TAGS)

        try:
            NAMESPACE.validate_namespace_not_used(names=tags.keys())
            tags_arr = [RunTag(key, str(value)) for key, value in tags.items()]
            self.mlflow_client.log_batch(
                run_id=self.run_id, metrics=[], params=[], tags=tags_arr
            )
        except MlflowException as e:
            raise MlFoundryException(e.message) from e
        logger.info("Tags set successfully")

    def get_tags(self) -> Dict[str, str]:
        """Returns all the tags set for the current `run`.

        Returns:
            Dict[str, str]: A dictionary containing tags. The keys in the dictionary
                are tag names and the values are corresponding tag values.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project"
        )
        run.set_tags({"nlp.framework": "Spark NLP"})
        print(run.get_tags())

        run.end()
        ```
        """
        amplitude.track(amplitude.Event.GET_TAGS)

        run = self.mlflow_client.get_run(self.run_id)
        return run.data.tags

    def __compute_whylogs_stats(self, df):
        """__compute_whylogs_stats.

        Args:
            df:
        """

        if not isinstance(df, pd.DataFrame):
            raise MlFoundryException(
                f"df is expected to be a pandas DataFrame but got {str(type(df))}"
            )

        profile_file_name = (
            "profile"
            + "_"
            + datetime.datetime.now().strftime(constants.TIME_FORMAT)
            + ".bin"
        )
        session = whylogs.get_or_create_session()
        profile = session.new_profile()
        profile.track_dataframe(df)
        profile.write_protobuf(profile_file_name)

        try:
            self.mlflow_client.set_tag(self.run_id, "whylogs", True)
            self.mlflow_client.log_artifact(
                self.run_id,
                profile_file_name,
                artifact_path=MlFoundryRun.S3_WHYLOGS_PATH,
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None

        if os.path.exists(profile_file_name):
            os.remove(profile_file_name)

    def auto_log_metrics(
        self,
        model_type: enums.ModelType,
        data_slice: enums.DataSlice,
        predictions: Collection[Any],
        actuals: Optional[Collection[Any]] = None,
        class_names: Optional[List[str]] = None,
        prediction_probabilities=None,
    ) -> ComputedMetrics:
        """auto_log_metrics.

        Args:
            model_type (enums.ModelType): model_type
            data_slice (enums.DataSlice): data_slice
            predictions (Collection[Any]): predictions
            actuals (Optional[Collection[Any]]): actuals
            class_names (Optional[List[str]]): class_names
            prediction_probabilities:

        Returns:
            ComputedMetrics:
        """
        metrics_calculator = get_metrics_calculator_v2(model_type)
        metrics = metrics_calculator.compute_metrics(
            predictions=predictions,
            actuals=actuals,
            prediction_probabilities=prediction_probabilities,
            class_names=class_names,
        )
        metric_path = os.path.join(constants.ALM_ARTIFACT_PATH, data_slice.value)
        log_artifact_blob(
            mlflow_client=self.mlflow_client,
            run_id=self.run_id,
            blob=metrics.json(),
            file_name=constants.ALM_METRICS_FILE_NAME,
            artifact_path=metric_path,
        )
        return metrics

    # TODO (nikunjbjj): This function is too long. Need to be broken into smaller testable modules.
    def log_dataset_stats(
        self,
        df,
        data_slice: enums.DataSlice,
        data_schema: Schema,
        model_type: enums.ModelType,
        shap_values=None,
    ):
        """log_dataset_stats.

        Args:
            df:
            data_slice (enums.DataSlice): data_slice
            data_schema (Schema): data_schema
            model_type (enums.ModelType): model_type
            shap_values:
        """
        logger.info("Computing and logging dataset stats, this might take a while ...")
        data_slice = enums.DataSlice(data_slice)
        model_type = enums.ModelType(model_type)

        if not isinstance(df, pd.DataFrame):
            raise MlFoundryException(f"Expected pd.DataFrame but got {str(type(df))}")

        if not data_schema.actual_column_name:
            raise MlFoundryException(f"Schema.actual_column_name cannot be None")
        elif not data_schema.prediction_column_name:
            raise MlFoundryException(f"Schema.prediction_column_name cannot be None")
        elif data_schema.feature_column_names is None:
            raise MlFoundryException(f"Schema.feature_column_names cannot be None")
        elif not isinstance(data_schema.feature_column_names, list):
            raise MlFoundryException(
                f"data_schema.feature_column_names should be of type list, "
                f"cannot be {type(data_schema.feature_column_names)}"
            )

        self.__compute_whylogs_stats(df[set(data_schema.feature_column_names)])

        if model_type in [
            enums.ModelType.BINARY_CLASSIFICATION,
            enums.ModelType.MULTICLASS_CLASSIFICATION,
        ]:
            class_names = None
            prediction_col_dtype, actual_col_dtype = (
                df[data_schema.prediction_column_name].dtype,
                df[data_schema.actual_column_name].dtype,
            )
            if prediction_col_dtype == object and actual_col_dtype != object:
                raise MlflowException(
                    "Both predictions column and actual column has to be of same datatype, either string or number"
                )
            elif prediction_col_dtype != object and actual_col_dtype == object:
                raise MlflowException(
                    "Both predictions column and actual column has to be of same datatype, either string or number"
                )
            elif prediction_col_dtype == object and actual_col_dtype == object:
                actual_class_names = df[data_schema.actual_column_name].unique()
                prediction_class_name = df[data_schema.prediction_column_name].unique()
                class_names = sorted(
                    set(actual_class_names) | set(prediction_class_name)
                )
                df[data_schema.actual_column_name] = df[
                    data_schema.actual_column_name
                ].apply(lambda x: class_names.index(x))
                df[data_schema.prediction_column_name] = df[
                    data_schema.prediction_column_name
                ].apply(lambda x: class_names.index(x))

        unique_count_dict = {}
        if model_type in [
            enums.ModelType.BINARY_CLASSIFICATION,
            enums.ModelType.MULTICLASS_CLASSIFICATION,
        ]:
            unique_count_dict[data_schema.prediction_column_name] = np.unique(
                df[data_schema.prediction_column_name].to_list(), return_counts=True
            )
            unique_count_dict[data_schema.actual_column_name] = np.unique(
                df[data_schema.actual_column_name].to_list(), return_counts=True
            )
        elif model_type == enums.ModelType.REGRESSION:
            session = whylogs.get_or_create_session()
            profile = session.new_profile()
            profile.track_dataframe(
                df[[data_schema.actual_column_name, data_schema.prediction_column_name]]
            )
            unique_count_dict[
                constants.ACTUAL_PREDICTION_COUNTS
            ] = profile.flat_summary()["hist"]

        if data_schema.categorical_feature_column_names:
            for feature in data_schema.categorical_feature_column_names:
                unique_count_dict[feature] = np.unique(
                    df[feature].to_list(), return_counts=True
                )

        unique_count_name = "unique_count" + "_" + str(data_slice.value) + ".json"
        constants.RUN_STATS_FOLDER.mkdir(parents=True, exist_ok=True)
        unique_count_path = os.path.join(constants.RUN_STATS_FOLDER, unique_count_name)

        with open(unique_count_path, "w") as fp:
            json.dump(unique_count_dict, fp, cls=NumpyEncoder)

        schema_json_name = "schema" + "_" + str(data_slice.value) + ".json"
        schema_json_path = os.path.join(constants.RUN_STATS_FOLDER, schema_json_name)

        with open(schema_json_path, "w") as outfile:
            json.dump(data_schema.__dict__, outfile)

        # TODO (nikunjbjj): This class name could be referenced before assignment. We need to fix this.
        if (
            model_type
            in [
                enums.ModelType.BINARY_CLASSIFICATION,
                enums.ModelType.MULTICLASS_CLASSIFICATION,
            ]
            and class_names is not None
        ):
            class_names_path = f"class_names_{data_slice.value}.json"
            class_names_path = constants.RUN_STATS_FOLDER / class_names_path
            class_names_dict = {"class_names": class_names}
            with open(class_names_path, "w") as fp:
                json.dump(class_names_dict, fp)

        metrics_class = get_metrics_calculator_v1(model_type)

        if data_schema.prediction_probability_column_name:
            metrics_dict = metrics_class.compute_metrics(
                df[set(data_schema.feature_column_names)],
                df[data_schema.prediction_column_name].to_list(),
                df[data_schema.actual_column_name].to_list(),
                df[data_schema.prediction_probability_column_name].to_list(),
            )
        else:
            metrics_dict = metrics_class.compute_metrics(
                df[set(data_schema.feature_column_names)],
                df[data_schema.prediction_column_name].to_list(),
                df[data_schema.actual_column_name].to_list(),
            )
        # non-multi dimensional metrics
        metrics_dict_with_data_slice = {}

        for key in metrics_dict[constants.NON_MULTI_DIMENSIONAL_METRICS].keys():
            new_key = "pre_computed_" + key + "_" + str(data_slice.value)
            metrics_dict_with_data_slice[new_key] = metrics_dict[
                constants.NON_MULTI_DIMENSIONAL_METRICS
            ][key]

        if shap_values is not None:
            tag_key = "data_stats_and_shap_" + data_slice.value
        else:
            tag_key = "data_stats_" + data_slice.value

        self.mlflow_client.set_tag(self.run_id, "modelType", model_type.value)
        self.mlflow_client.set_tag(self.run_id, tag_key, True)
        self.log_metrics(metrics_dict_with_data_slice)

        constants.RUN_METRICS_FOLDER.mkdir(parents=True, exist_ok=True)
        multi_dimension_metric_file = (
            "pre_computed_"
            + constants.MULTI_DIMENSIONAL_METRICS
            + "_"
            + str(data_slice.value)
            + ".json"
        )
        multi_dimension_metric_file_path = os.path.join(
            constants.RUN_METRICS_FOLDER, multi_dimension_metric_file
        )

        with open(multi_dimension_metric_file_path, "w") as fp:
            json.dump(
                metrics_dict[constants.MULTI_DIMENSIONAL_METRICS], fp, cls=NumpyEncoder
            )

        if model_type == enums.ModelType.TIMESERIES:
            actuals_predictions_filename = (
                "actuals_predictions_" + str(data_slice.value) + ".parquet"
            )
            actuals_predictions_filepath = os.path.join(
                constants.RUN_STATS_FOLDER, actuals_predictions_filename
            )
            df[
                [data_schema.prediction_column_name, data_schema.actual_column_name]
            ].to_parquet(actuals_predictions_filepath)

        try:

            # with self.mlflow_run as run:
            self.mlflow_client.log_artifact(
                self.run_id, unique_count_path, artifact_path=MlFoundryRun.S3_STATS_PATH
            )
            self.mlflow_client.log_artifact(
                self.run_id,
                multi_dimension_metric_file_path,
                artifact_path=MlFoundryRun.S3_METRICS_PATH,
            )
            self.mlflow_client.log_artifact(
                self.run_id, schema_json_path, artifact_path=MlFoundryRun.S3_STATS_PATH
            )
            if (
                model_type
                in [
                    enums.ModelType.BINARY_CLASSIFICATION,
                    enums.ModelType.MULTICLASS_CLASSIFICATION,
                ]
                and class_names is not None
            ):
                self.mlflow_client.log_artifact(
                    self.run_id,
                    class_names_path,
                    artifact_path=MlFoundryRun.S3_STATS_PATH,
                )
            # TODO (nikunjbjj): This class name path and actuals_predictions_filepath could be referenced
            #  before assignment. We need to fix this.
            if model_type == enums.ModelType.TIMESERIES:
                self.mlflow_client.log_artifact(
                    self.run_id,
                    actuals_predictions_filepath,
                    artifact_path=MlFoundryRun.S3_STATS_PATH,
                )
                os.remove(actuals_predictions_filepath)
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None

        os.remove(multi_dimension_metric_file_path)
        os.remove(schema_json_path)
        os.remove(unique_count_path)

        if shap_values is not None:
            self.__log_shap_values(
                df[set(data_schema.feature_column_names)], shap_values, data_slice
            )

        logger.info("Dataset stats computed and logged successfully")

    def __log_shap_values(self, df, shap_values: list, data_slice: enums.DataSlice):
        """__log_shap_values.

        Args:
            df:
            shap_values (list): shap_values
            data_slice (enums.DataSlice): data_slice
        """

        if not isinstance(df, pd.DataFrame):
            raise MlFoundryException(f"Expected pd.DataFrame but got {str(type(df))}")

        artifact_name = str(self.run_id) + "_" + str(data_slice.value) + "_shap.json"
        constants.RUN_STATS_FOLDER.mkdir(parents=True, exist_ok=True)
        filename = os.path.join(constants.RUN_STATS_FOLDER, artifact_name)

        shap_values_dict = {"shap_values": shap_values}

        with open(filename, "w") as fp:
            json.dump(shap_values_dict, fp, cls=NumpyEncoder)

        try:
            self.mlflow_client.log_artifact(
                self.run_id, filename, artifact_path=MlFoundryRun.S3_STATS_PATH
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None

        os.remove(filename)

    def get_metrics(
        self, metric_names: Optional[Iterable[str]] = None
    ) -> Dict[str, List[Metric]]:
        """Get metrics logged for the current `run` grouped by metric name.

        Args:
            metric_names (Optional[Iterable[str]], optional): A list of metric names
                For which the logged metrics will be fetched. If not passed, then all
                metrics logged under the `run` is returned.

        Returns:
            Dict[str, List[Metric]]: A dictionary containing metric name to list of metrics
                map.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        )
        run.log_metrics(metric_dict={"accuracy": 0.7, "loss": 0.6}, step=0)
        run.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4}, step=1)

        metrics = run.get_metrics()
        for metric_name, metric_history in metrics.items():
            print(f"logged metrics for metric {metric_name}:")
            for metric in metric_history:
                print(f"value: {metric.value}")
                print(f"step: {metric.step}")
                print(f"timestamp_ms: {metric.timestamp}")
                print("--")

        run.end()
        ```
        """
        amplitude.track(amplitude.Event.GET_METRICS)
        run = self.mlflow_client.get_run(self.run_id)
        run_metrics = run.data.metrics

        metric_names = (
            set(metric_names) if metric_names is not None else run_metrics.keys()
        )

        unknown_metrics = metric_names - run_metrics.keys()
        if len(unknown_metrics) > 0:
            logger.warning(f"{unknown_metrics} metrics not present in the run")
        metrics_dict = {metric_name: [] for metric_name in unknown_metrics}
        valid_metrics = metric_names - unknown_metrics
        for metric_name in valid_metrics:
            metrics_dict[metric_name] = self.mlflow_client.get_metric_history(
                self.run_id, metric_name
            )
        return metrics_dict

    def get_params(self) -> Dict[str, str]:
        """Get all the params logged for the current `run`.

        Returns:
            Dict[str, str]: A dictionary containing the parameters. The keys in the dictionary
                are parameter names and the values are corresponding parameter values.

        Examples:
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project"
        )
        run.log_params({"learning_rate": 0.01, "epochs": 10})
        print(run.get_params())

        run.end()
        ```
        """
        amplitude.track(amplitude.Event.GET_PARAMS)
        run = self.mlflow_client.get_run(self.run_id)
        return run.data.params

    def get_model(self, dest_path: Optional[str] = None, **kwargs):
        """
        Deserialize and return the logged model object for the current `run`.

        Args:
            dest_path (Optional[str], optional): The path where the model is
            downloaded before deserializing.
            kwargs: Keyword arguments to be passed to the de-serializer.
        """
        return self._model_driver.get_model(dest_path=dest_path, **kwargs)

    def download_model(self, dest_path: str):
        """
        Download logged model for the current `run` in a local directory.

        Args:
            dest_path (str): local directory where the model will be downloaded.
                if `dest_path` does not exist, it will be created.
                If dest_path already exist, it should be an empty directory.
        """
        return self._model_driver.download_model(dest_path=dest_path)

    def log_model(self, model, framework: Union[enums.ModelFramework, str], **kwargs):
        """
        Serialize and log a model under for the current `run`. After logging, we
        cannot overwrite it.

        Args:
            model: The model object
            framework (Union[enums.ModelFramework, str]): Model Framework. Ex:- pytorch,
                sklearn, tensorflow etc. The full list of supported frameworks can be
                found in `mlfoundry.enums.ModelFramework`.
            kwargs: Keyword arguments to be passed to the serializer.

        Examples:
        ### sklearn
        ```python
        import mlfoundry
        import numpy as np
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        run = client.create_run(
            project_name="my-classification-project"
        )
        X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
        y = np.array([1, 1, 2, 2])
        clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
        clf.fit(X, y)

        run.log_model(clf, "sklearn")
        """
        self._model_driver.log_model(model=model, framework=framework, **kwargs)
