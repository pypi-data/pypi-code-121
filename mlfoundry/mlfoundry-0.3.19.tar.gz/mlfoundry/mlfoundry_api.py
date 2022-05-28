"""
# TO independently test this module, you can run the example in the path
python examples/sklearn/iris_train.py

Besides running pytest
"""
import datetime
import logging
import os
import urllib
from functools import partial
from typing import Any, Dict, List, Optional

import human_id
import mlflow
import pandas as pd
from mlflow.entities import ViewType
from mlflow.store.artifact.artifact_repository_registry import (
    _artifact_repository_registry,
)
from mlflow.tracking import MlflowClient

from mlfoundry import amplitude, constants
from mlfoundry.artifact.truefoundry_artifact_repo import TruefoundryArtifactRepository
from mlfoundry.exceptions import MlflowException, MlFoundryException
from mlfoundry.inference.store import (
    ActualPacket,
    InferencePacket,
    InferenceStoreClient,
    ValueType,
    get_inference_store,
)
from mlfoundry.internal_namespace import NAMESPACE
from mlfoundry.mlfoundry_run import MlFoundryRun
from mlfoundry.run_utils import resolve_tracking_uri
from mlfoundry.session import Session
from mlfoundry.tracking.auth_service import AuthService
from mlfoundry.tracking.truefoundry_rest_store import get_rest_store

logger = logging.getLogger(__name__)


def init_rest_tracking(tracking_uri: str, api_key: Optional[str]):
    """init_rest_tracking.

    Args:
        tracking_uri (str): tracking_uri
        api_key (Optional[str]): api_key
    """
    rest_store = get_rest_store(tracking_uri)
    auth_service = AuthService(tenant_info=rest_store.get_tenant_info())

    session = Session(auth_service=auth_service, tracking_uri=tracking_uri)
    session.init_session(api_key)

    artifact_repository = partial(TruefoundryArtifactRepository, rest_store=rest_store)
    _artifact_repository_registry.register("s3", artifact_repository)


def get_client(
    tracking_uri: Optional[str] = None,
    inference_store_uri: Optional[str] = None,
    disable_analytics: bool = False,
    api_key: Optional[str] = None,
) -> "MlFoundry":
    """Initializes and returns the mlfoundry client.

    Args:
        tracking_uri (Optional[str], optional): Custom tracking server URL.
            If not passed, by default all the run details are sent to Truefoundry server
            and can be visualized at https://app.truefoundry.com/mlfoundry.
            Tracking server URL can be also configured using the `MLF_HOST`
            environment variable. In case environment variable and argument is passed,
            the URL passed via this argument will take precedence.
        disable_analytics (bool, optional): To turn off usage analytics collection, pass `True`.
            By default, this is set to `False`.
        api_key (Optional[str], optional): API key.
            API key can be found at https://app.truefoundry.com/settings. API key can be
            also configured using the `MLF_API_KEY` environment variable. In case the
            environment variable and argument are passed, the value passed via this argument
            will take precedence.

    Returns:
        MlFoundry: Instance of `MlFoundry` class which represents a `run`.

    Examples:
    ### Get client
    Set the API key using the `MLF_API_KEY` environment variable.
    ```
    export MLF_API_KEY="MY-API_KEY"
    ```

    We can then initialize the client, the API key will be picked up from the
    environment variable.
    ```python
    import mlfoundry

    client = mlfoundry.get_client()
    ```

    ### Get client with API key passed via argument.
    ```python
    import mlfoundry

    API_KEY = "MY-API_KEY"
    client = mlfoundry.get_client(api_key=API_KEY)
    ```
    """
    # TODO (chiragjn): Will potentially need to make MlFoundry (and possibly MlFoundryRun) a Singleton instance.
    #                  Since this sets the tracking URI in global namespace, if someone were to call
    #                  get_client again with different tracking uri, the ongoing run's data will start getting
    #                  pushed to another datastore. Or we should not allow passing in tracking URI and just have
    #                  fixed online and offline clients
    amplitude.init(disable_analytics)
    tracking_uri = resolve_tracking_uri(tracking_uri)
    if tracking_uri.startswith("file:"):
        tracking_uri = os.path.join(tracking_uri, constants.MLRUNS_FOLDER_NAME)
    else:
        init_rest_tracking(tracking_uri=tracking_uri, api_key=api_key)
    amplitude.track(
        amplitude.Event.GET_CLIENT,
        # tracking whether user is using file:// or https://
        event_properties={
            "tracking_scheme": urllib.parse.urlparse(tracking_uri).scheme
        },
    )
    return MlFoundry(tracking_uri, inference_store_uri=inference_store_uri)


class MlFoundry:
    """MlFoundry."""

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        inference_store_uri: Optional[str] = None,
    ):
        """__init__.

        Args:
            tracking_uri (Optional[str], optional): tracking_uri
            inference_store_uri (Optional[str], optional): inference_store_uri
        """
        try:
            mlflow.set_tracking_uri(tracking_uri)
        except MlflowException as e:
            err_msg = (
                f"Could not initialise mlfoundry object. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e

        self.mlflow_client = MlflowClient()
        self.inference_store_client: Optional[InferenceStoreClient] = (
            InferenceStoreClient(lambda: get_inference_store(inference_store_uri))
            if inference_store_uri is not None
            else None
        )

    def _get_or_create_project(self, project_name: str, owner: Optional[str]) -> str:
        """_get_or_create_experiment.

        Args:
            project_name (str): The name of the project.
            owner (Optional[str], optional): Owner of the project. If owner is not passed,
                the current user will be used as owner. If the given owner
                does not have the project, it will be created under
                the current user.

        Returns:
            str: The id of the project.
        """
        experiment_name = project_name
        try:
            experiment = self.mlflow_client.get_experiment_by_name(
                experiment_name, owner_subject_id=owner
            )
            if experiment is not None:
                return experiment.experiment_id
            if not owner:
                logger.info(
                    f"project {experiment_name} does not exist. Creating {experiment_name}."
                )
                return self.mlflow_client.create_experiment(experiment_name)
            else:
                logger.warning(
                    f"project {experiment_name} under owner {owner} does not exist. "
                    "looking for project under current user."
                )
                return self._get_or_create_project(
                    project_name=project_name, owner=None
                )
        except MlflowException as e:
            err_msg = (
                f"Error happened in creating or getting project based on project name: "
                f"{experiment_name}. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e

    def get_all_projects(self) -> List[str]:
        """Returns a list of project ids accessible by the current user.

        Returns:
            List[str]: A list of project ids.
        """
        amplitude.track(amplitude.Event.GET_ALL_PROJECTS)
        try:
            experiments = self.mlflow_client.list_experiments(view_type=ViewType.ALL)
        except MlflowException as e:
            err_msg = (
                f"Error happened in fetching project names. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e

        projects = []
        for e in experiments:
            # Experiment ID 0 represents default project which we are removing.
            if e.experiment_id != "0":
                projects.append(e.name)

        return projects

    def create_run(
        self,
        project_name: str,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        owner: Optional[str] = None,
        log_system_metrics: bool = True,
        **kwargs,
    ) -> MlFoundryRun:
        """Initialize a `run`.

        In a machine learning experiment `run` represents a single experiment
        conducted under a project.
        Args:
            project_name (str): The name of the project under which the run will be created.
                project_name should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
                The user must have `ADMIN` or `WRITE` access to this project.
            run_name (Optional[str], optional): The name of the run. If not passed, a randomly
                generated name is assigned to the run. Under a project, all runs should have
                a unique name. If the passed `run_name` is already used under a project, the
                `run_name` will be de-duplicated by adding a suffix.
                run name should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
            tags (Optional[Dict[str, Any]], optional): Optional tags to attach with
                this run. Tags are key-value pairs.
            owner (Optional[str], optional): Owner of the project. If owner is not passed,
                the current user will be used as owner. If the given owner
                does not have the project, it will be created under
                the current user.
            log_system_metrics (bool, optional): Automatically collect system metrics. By default, this is
                set to `True`.
            kwargs:

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:
        ### Create a run under current user.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()

        tags = {"model_type": "svm"}
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel", tags=tags
        )

        run.end()
        ```

        ### Creating a run using context manager.
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

        ### Create a run in a project owned by a different user.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()

        tags = {"model_type": "svm"}
        run = client.create_run(
            project_name="my-classification-project",
            run_name="svm-with-rbf-kernel",
            tags=tags,
            owner="bob",
        )
        run.end()
        ```
        """
        amplitude.track(amplitude.Event.CREATE_RUN)
        if not run_name:
            run_name = human_id.generate_id(word_count=3)
        if project_name == "" or (not isinstance(project_name, str)):
            raise MlFoundryException(
                f"project_name must be string type and not empty. "
                f"Got {type(project_name)} type with value {project_name!r}"
            )

        experiment_id = self._get_or_create_project(project_name, owner=owner)

        if tags is not None:
            NAMESPACE.validate_namespace_not_used(tags.keys())
        else:
            tags = {}

        run = self.mlflow_client.create_run(experiment_id, name=run_name, tags=tags)
        mlf_run_id = run.info.run_id

        mlf_run = MlFoundryRun(
            experiment_id, mlf_run_id, log_system_metrics=log_system_metrics, **kwargs
        )
        mlf_run._add_git_info()
        logger.info(f"Run is created with name {run.info.name!r} and id {mlf_run_id!r}")
        return mlf_run

    def get_run(self, run_id: str) -> MlFoundryRun:
        """Get an existing `run` by the `run_id`.

        Args:
            run_id (str): run_id of an existing `run`.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.
        """
        amplitude.track(amplitude.Event.GET_RUN)
        if run_id == "" or (not isinstance(run_id, str)):
            raise MlFoundryException(
                f"run_id must be string type and not empty. "
                f"Got {type(run_id)} type with value {run_id}"
            )

        run = self.mlflow_client.get_run(run_id)
        experiment_id = run.info.experiment_id
        return MlFoundryRun(experiment_id, run.info.run_id, log_system_metrics=False)

    def get_run_by_fqn(self, run_fqn: str) -> MlFoundryRun:
        """Get an existing `run` by `fqn`.

        `fqn` stands for Fully Qualified Name. A run `fqn` has the following pattern:
        owner/project_name/run_name

        If user `bob` has created a run `svm` under the project `cat-classifier`,
        the `fqn` will be `bob/cat-classifier/svm`.

        Args:
            run_fqn (str): `fqn` of an existing run.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.
        """
        run = self.mlflow_client.get_run_by_fqn(run_fqn)
        return MlFoundryRun(
            experiment_id=run.info.experiment_id,
            run_id=run.info.run_id,
            log_system_metrics=False,
        )

    def get_all_runs(
        self, project_name: str, owner: Optional[str] = None
    ) -> pd.DataFrame:
        """Returns all the run name and id present under a project.

        The user must have `READ` access to the project.
        Args:
            project_name (str): Name of the project.
            owner (Optional[str], optional): Owner of the project. If owner is not passed,
                                   the current user will be used as owner.
        Returns:
            pd.DataFrame: dataframe with two columns- run_id and run_name
        """
        amplitude.track(amplitude.Event.GET_ALL_RUNS)
        if project_name == "" or (not isinstance(project_name, str)):
            raise MlFoundryException(
                f"project_name must be string type and not empty. "
                f"Got {type(project_name)} type with value {project_name}"
            )
        experiment = self.mlflow_client.get_experiment_by_name(
            project_name, owner_subject_id=owner
        )
        if experiment is None:
            return pd.DataFrame(
                columns=[constants.RUN_ID_COL_NAME, constants.RUN_NAME_COL_NAME]
            )

        experiment_id = experiment.experiment_id

        try:
            all_run_infos = self.mlflow_client.list_run_infos(
                experiment_id, run_view_type=ViewType.ALL
            )
        except MlflowException as e:
            err_msg = f"Error happened in while fetching runs for project {project_name}. Error details: {e.message}"
            raise MlFoundryException(err_msg) from e

        runs = []

        for run_info in all_run_infos:
            try:
                run = self.mlflow_client.get_run(run_info.run_id)
                run_name = run.info.name or run.data.tags.get(
                    constants.RUN_NAME_COL_NAME, ""
                )
                runs.append((run_info.run_id, run_name))
            except MlflowException as e:
                logger.warning(
                    f"Could not fetch details of run with run_id {run_info.run_id}. "
                    f"Skipping this one. Error details: {e.message}. "
                )

        return pd.DataFrame(
            runs, columns=[constants.RUN_ID_COL_NAME, constants.RUN_NAME_COL_NAME]
        )

    @staticmethod
    def get_tracking_uri():
        """get_tracking_uri."""
        return mlflow.tracking.get_tracking_uri()

    def log_prediction(
        self,
        model_name: str,
        model_version: str,
        inference_id: str,
        features: ValueType,
        predictions: ValueType,
        raw_data: Optional[ValueType] = None,
        actuals: Optional[ValueType] = None,
        occurred_at: Optional[int] = None,
    ):
        """log_prediction.

        Args:
            model_name (str): model_name
            model_version (str): model_version
            inference_id (str): inference_id
            features (ValueType): features
            predictions (ValueType): predictions
            raw_data (Optional[ValueType]): raw_data
            actuals (Optional[ValueType]): actuals
            occurred_at (Optional[int]): occurred_at
        """
        if self.inference_store_client is None:
            raise MlFoundryException(
                "Pass inference_store_uri in get_client function to use log_prediction"
            )
        if occurred_at is None:
            occurred_at = datetime.datetime.utcnow()
        elif not isinstance(occurred_at, int):
            raise TypeError("occurred_at should be unix epoch")
        else:
            occurred_at = datetime.datetime.utcfromtimestamp(occurred_at)
        inference_packet = InferencePacket(
            model_name=model_name,
            model_version=model_version,
            features=features,
            predictions=predictions,
            inference_id=inference_id,
            raw_data=raw_data,
            actuals=actuals,
            occurred_at=occurred_at,
        )
        self.inference_store_client.log_predictions([inference_packet])

    def log_actuals(self, model_name: str, inference_id: str, actuals: ValueType):
        """log_actuals.

        Args:
            model_name (str): model_name
            inference_id (str): inference_id
            actuals (ValueType): actuals
        """
        if self.inference_store_client is None:
            raise MlFoundryException(
                "Pass inference_store_uri in get_client function to use log_prediction"
            )
        actuals_packet = ActualPacket(
            model_name=model_name, inference_id=inference_id, actuals=actuals
        )
        self.inference_store_client.log_actuals([actuals_packet])
