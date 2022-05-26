import logging
import os
import posixpath
import re
import tempfile
import typing
from distutils.dir_util import copy_tree

import mlflow
from mlflow.entities import RunLog, RunStatus
from mlflow.tracking import MlflowClient

from mlfoundry.enums import ModelFramework
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.frameworks import get_model_registry
from mlfoundry.log_types import ModelArtifactRunLog

MODEL_PREFIX = posixpath.join("mlf", "run-logs", "models")
MODEL_NAME_REGEX = re.compile(r"^[a-zA-Z0-9-_]*$")
logger = logging.getLogger(__name__)

# Right now we do not have concept of a model name.
# Now while saving the model as a run log, we need to give a key name.
# Right now I am hardcoding it to "model".
# This is not exposed to user at all.
# We should not change this default value at all.
DEFAULT_MODEL_NAME = "model"


def load_model_from_local_path(local_path: str):
    # this will fail if the model was not serialized
    # using tfy-mlflow-client
    # test all flavors from here

    model = mlflow.models.Model.load(local_path)
    for flavor in model.flavors.keys():
        try:
            framework = ModelFramework(flavor)
        except Exception:
            continue
        registry = get_model_registry(framework)
        return registry.load_model(local_path)
    raise MlFoundryException(f"unsupported frameworks {model.flavors.keys()}")


class ModelDriver:
    """ModelDriver."""

    def __init__(self, mlflow_client: MlflowClient, run_id: str):
        """__init__.

        :param mlflow_client:
        :type mlflow_client: MlflowClient
        :param run_id:
        :type run_id: str
        """
        self.mlflow_client: MlflowClient = mlflow_client
        self.run_id: str = run_id

    def _get_run_log(self, model_name: str) -> typing.Optional[RunLog]:
        """
        Get run log under a run for a model
        If there are no run log then this function will return None.

        :param model_name: Name of the model. This will be just DEFAULT_MODEL_NAME
                           for now.
        :type model_name: str
        :rtype: typing.Optional[RunLog]
        """
        run_logs = self.mlflow_client.list_run_logs(
            run_uuid=self.run_id,
            key=model_name,
            log_type=ModelArtifactRunLog.get_log_type(),
        )
        if len(run_logs) == 0:
            return None
        return run_logs[0]

    def log_model(self, model, framework: str, **kwargs):
        """
        Serialize and log a model under a run. After logging, we
        cannot overwrite it.

        :param model: The model object
        :param framework: Model Framework. Ex:- pytorch, sklearn
        :type framework: str
        :param kwargs: Keyword arguments to be passed to the serializer.
        """
        model_name = DEFAULT_MODEL_NAME
        run_log = self._get_run_log(model_name)
        if run_log is not None:
            raise MlFoundryException("Model already logged, cannot overwrite")
        framework = ModelFramework(framework)
        artifact_path = posixpath.join(MODEL_PREFIX, model_name)
        # TODO (chiragjn): This is hack to temporarily use the mlflow.fluent API because
        #                  .log_model relies on run_id being stored in mlflow's global run stack
        created_run = None
        try:
            # Add to mlflow.fluent's global stack, hoping no other fluent run is running parallely
            created_run = mlflow.start_run(
                run_id=self.run_id,
                nested=True,  # necessary to avoid messing with existing run stack
            )
            get_model_registry(framework).log_model(
                model, artifact_path=artifact_path, **kwargs
            )
        finally:
            if created_run:
                # Remove from mlflow.fluent's global stack but keeping the run in Running mode
                mlflow.end_run(RunStatus.to_string(RunStatus.RUNNING))

        model_artifact_log = ModelArtifactRunLog(
            artifact_path=artifact_path, framework=framework
        )
        run_log = model_artifact_log.to_run_log(key=model_name)
        self.mlflow_client.insert_run_logs(run_uuid=self.run_id, run_logs=[run_log])
        logger.info("Model logged successfully")

    def get_model(self, dest_path: typing.Optional[str] = None, **kwargs):
        """
        Deserialize and return the logged model object.
        dest_path is used to download the model before it is deserialized.
        Apart from model_name and dest_path, all the other keyword args (kwargs)
        will be passed to the deserializer.

        :param dest_path: The path where the model is downloaded before deserializing.
        :type dest_path: typing.Optional[str]
        :param kwargs: Keyword arguments to be passed to the deserializer.
        """
        model_name = DEFAULT_MODEL_NAME
        run_log = self._get_run_log(model_name)
        if run_log is None:
            raise MlFoundryException("Model is not logged")

        model_artifact_log = ModelArtifactRunLog.from_run_log(run_log)
        model_uri = self.mlflow_client.download_artifacts(
            self.run_id, path=model_artifact_log.artifact_path, dst_path=dest_path
        )
        model_framework = get_model_registry(model_artifact_log.framework)
        return model_framework.load_model(
            model_uri,
            **kwargs,
        )

    def download_model(self, dest_path: str):
        """
        Download logged model for a run in a local directory.
        If dest_path does not exist, a new directory will be created.
        If dest_path already exist, it should be an empty directory.

        :param dest_path: local directory where the model will be downloaded.
        :type dest_path: str
        """
        model_name = DEFAULT_MODEL_NAME
        run_log = self._get_run_log(model_name)
        if run_log is None:
            raise MlFoundryException("Model is not logged")

        model_artifact_log = ModelArtifactRunLog.from_run_log(run_log)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        elif any(os.scandir(dest_path)):
            raise MlFoundryException("model download path should be empty")
        with tempfile.TemporaryDirectory() as local_dir:
            self.mlflow_client.download_artifacts(
                self.run_id, path=model_artifact_log.artifact_path, dst_path=local_dir
            )
            model_dir = os.path.join(
                local_dir, os.path.normpath(model_artifact_log.artifact_path)
            )
            copy_tree(model_dir, dest_path)
