from typing import Dict, List, Tuple

from openapi_client import ResponseSweepExperimentInfo
from openapi_client.models import (
    InfluxdbSweepLog,
    OrmEarlyStoppingSetting,
    OrmEarlyStoppingSpec,
    OrmHyperparameter,
    OrmParameter,
    OrmSweepObjective,
    OrmSweepSearchSpace,
    ResponseSweepInfo,
    ResponseSweepListResponse,
    SweepCreateAPIInput,
)
from vessl import vessl_api
from vessl.kernel_cluster import read_cluster
from vessl.kernel_resource_spec import (
    _configure_custom_kernel_resource_spec,
    read_kernel_resource_spec,
)
from vessl.organization import _get_organization_name
from vessl.project import _get_project_name
from vessl.util.constant import MOUNT_PATH_OUTPUT, SWEEP_OBJECTIVE_TYPE_MAXIMIZE
from vessl.util.exception import InvalidTypeError
from vessl.volume import _configure_volume_mount_requests


def read_sweep(sweep_name: str, **kwargs) -> ResponseSweepInfo:
    """Read sweep in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        sweep_name(str): Sweep name.

    Example:
        ```python
        vessl.read_sweep(
            sweep_name="pitch-lord",
        )
        ```
    """
    return vessl_api.sweep_read_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        sweep=sweep_name,
    )


def list_sweeps(**kwargs) -> List[ResponseSweepListResponse]:
    """List sweeps in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Example:
        ```python
        vessl.list_sweeps()
        ```
    """
    return vessl_api.sweep_list_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    ).results


def create_sweep(
    objective: OrmSweepObjective,
    max_experiment_count: int,
    parallel_experiment_count: int,
    max_failed_experiment_count: int,
    algorithm: str,
    parameters: List[OrmParameter],
    cluster_name: str,
    start_command: str,
    kernel_resource_spec_name: str = None,
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: float = None,
    gpu_type: str = None,
    gpu_limit: int = None,
    kernel_image_url: str = None,
    *,
    early_stopping_name: str = None,
    early_stopping_settings: List[Tuple[str, str]] = None,
    message: str = None,
    hyperparameters: List[Tuple[str, str]] = None,
    dataset_mounts: List[str] = None,
    git_ref_mounts: List[str] = None,
    git_diff_mount: str = None,
    archive_file_mount: str = None,
    root_volume_size: str = None,
    working_dir: str = None,
    output_dir: str = MOUNT_PATH_OUTPUT,
    **kwargs,
) -> ResponseSweepInfo:
    """Create sweep in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`. Pass `use_git_diff=True` if you want to run
    experiment with uncommitted changes and pass `use_git_diff_untracked=True`
    if you want to run untracked changes(only valid if `use_git_diff` is set).

    Args:
        objective(OrmSweepObjective): A sweep objective including goal, metric,
            and type.
        max_experiment_count(int): The maximum number of experiments to run.
        parallel_experiment_count(int): The number of experiments to run in
            parallel.
        max_failed_experiment_count(int): The maximum number of experiments to
            allow to fail.
        algorithm(str): Parameter suggestion algorithm. `grid`, `random`, or
            `bayesian`.
        parameters(List[OrmParameter]): A list of parameters to search.
        cluster_name(str): Cluster name(must be specified before other options).
        start_command(str): Start command to execute in experiment container.
        kernel_resource_spec_name(str):  Resource type to run an experiment (for
            managed cluster only). Defaults to None.
        processor_type(str) cpu or gpu (for custom cluster only). Defaults to
            None.
        cpu_limit(float): Number of vCPUs (for custom cluster only). Defaults to
            None.
        memory_limit(str): Memory limit in GiB (for custom cluster only).
            Defaults to None.
        gpu_type(str): GPU type (for custom cluster only). Defaults to None.
        gpu_limit(int): Number of GPU cores (for custom cluster only). Defaults
            to None.
        kernel_image_url(str): Kernel docker image URL. Defaults to None.
        early_stopping_name(str): Early stopping algorithm name. Defaults to
            None.
        early_stopping_settings(List[Tuple[str, str]]): Early stopping algorithm
            settings. Defaults to None.
        message(str): Message. Defaults to None.
        hyperparameters(List[str]): A list of hyperparameters. Defaults to None.
        dataset_mounts(List[str]): A list of dataset mounts. Defaults to None.
        git_ref_mounts(List[str]): A list of git repository mounts. Defaults to
            None.
        git_diff_mount(str): Git diff mounts. Defaults to None.
        archive_file_mount(str): Local archive file mounts. Defaults to None.
        root_volume_size(str): Root volume size. Defaults to None.
        working_dir(str): Working directory path. Defaults to None.
        output_dir(str): Output directory path. Defaults to "/output/".

    Example:
        ```python
        sweep_objective = vessl.SweepObjective(
            type="maximize",
            goal="0.99",
            metric="val_accuracy",
        )

        parameters = [
            vessl.SweepParameter(
                name="optimizer",
                type="categorical",
                range=vessl.SweepParameterRange(
                    list=["adam", "sgd", "adadelta"]
                )
            ),
            vessl.SweepParameter(
                name="batch_size",
                type="int",
                range=vessl.SweepParameterRange(
                    max="256",
                    min="64",
                    step="8",
                )
            )
        ]

        vessl.create_sweep(
            objective=sweep_objective,
            max_experiment_count=4,
            parallel_experiment_count=2,
            max_failed_experiment_count=2,
            algorithm="random",
            parameters=parameters,
            dataset_mounts=[/input:mnist],
            cluster_name="aws-apne2-prod1",
            kernel_resource_spec_name="v1.cpu-4.mem-13",
            kernel_image_url="public.ecr.aws/vessl/kernels:py36.full-cpu",
            start_command="pip install requirements.txt && python main.py",
        )
        ```
    """
    cluster = read_cluster(cluster_name)

    kernel_resource_spec = kernel_resource_spec_id = None
    if cluster.is_savvihub_managed:  # TODO: rename to vessl
        kernel_resource_spec_id = read_kernel_resource_spec(
            cluster.id,
            kernel_resource_spec_name,
        ).id
    else:
        kernel_resource_spec = _configure_custom_kernel_resource_spec(
            processor_type,
            cpu_limit,
            memory_limit,
            gpu_type,
            gpu_limit,
        )

    early_stopping_spec = OrmEarlyStoppingSpec(
        algorithm_name=early_stopping_name,
        algorithm_settings=[
            OrmEarlyStoppingSetting(name=k, value=str(v))
            for k, v in (early_stopping_settings or [])
        ],
    )

    volume_mount_requests = _configure_volume_mount_requests(
        dataset_mounts=dataset_mounts,
        git_ref_mounts=git_ref_mounts,
        git_diff_mount=git_diff_mount,
        archive_file_mount=archive_file_mount,
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        output_dir=output_dir,
        **kwargs,
    )

    return vessl_api.sweep_create_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        sweep_create_api_input=SweepCreateAPIInput(
            objective=objective,
            max_experiment_count=max_experiment_count,
            parallel_experiment_count=parallel_experiment_count,
            max_failed_experiment_count=max_failed_experiment_count,
            algorithm=algorithm,
            search_space=OrmSweepSearchSpace(
                parameters=parameters,
            ),
            cluster_id=cluster.id,
            hyperparameters=[
                OrmHyperparameter(key, str(value))
                for key, value in map(
                    lambda hyperparameter: hyperparameter.split("="),
                    (hyperparameters or []),
                )
            ],
            image_url=kernel_image_url,
            early_stopping_spec=early_stopping_spec,
            message=message,
            resource_spec=kernel_resource_spec,
            resource_spec_id=kernel_resource_spec_id,
            start_command=start_command,
            volumes=volume_mount_requests,
        ),
    )


def terminate_sweep(sweep_name: str, **kwargs) -> ResponseSweepInfo:
    """Terminate sweep in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        sweep_name(str): Sweep name.

    Example:
        ```python
        vessl.terminate_sweep(
            sweep_name="pitch-lord",
        )
        ```
    """
    return vessl_api.sweep_terminate_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        sweep=sweep_name,
    )


def list_sweep_logs(
    sweep_name: str, tail: int = 200, **kwargs
) -> List[InfluxdbSweepLog]:
    """List sweep logs in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        sweep_name(str): Sweep name.
        tail(int): The number of lines to display from the end. Display all if
            -1. Defaults to 200.

    Example:
        ```python
        vessl.list_sweep_logs(
            sweep_name="pitch-lord",
        )
        ```
    """

    if tail == -1:
        tail = None

    return vessl_api.sweep_logs_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        sweep=sweep_name,
        limit=tail,
    ).logs


def get_best_sweep_experiment(sweep_name: str, **kwargs) -> ResponseSweepExperimentInfo:
    """Read sweep and return the best experiment info in the default
    organization/project. If you want to override the default
    organization/project, then pass `organization_name` or `project_name` as
    `**kwargs`.

    Args:
        sweep_name(str): Sweep name.

    Example:
        ```python
        vessl.get_best_sweep_experiment(
            sweep_name="pitch-lord",
        )
        ```
    """

    sweep_read_response = vessl_api.sweep_read_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        sweep=sweep_name,
    )
    if type(sweep_read_response) != ResponseSweepInfo:
        return sweep_read_response

    def best_experiments(
        items: [ResponseSweepExperimentInfo], maximize: bool
    ) -> ResponseSweepExperimentInfo:
        return sorted(
            items, key=lambda x: x.objective_metric_value, reverse=maximize
        ).pop()

    if sweep_read_response.experiment_summary.total > 0:
        filtered_experiment_summary = []
        for experiment in sweep_read_response.experiment_summary.sweep_experiment_infos:
            if not experiment.objective_metric_value:
                continue
            elif not isinstance(experiment.objective_metric_value, (int, float)):
                raise InvalidTypeError(
                    f"The type of experiment objective metric value is "
                    f"not integer or float: "
                    f"{type(experiment.objective_metric_value)}"
                )
            filtered_experiment_summary.append(experiment)

        if sweep_read_response.objective.type == SWEEP_OBJECTIVE_TYPE_MAXIMIZE:
            return best_experiments(filtered_experiment_summary, True)
        else:
            return best_experiments(filtered_experiment_summary, False)

    return ResponseSweepExperimentInfo()
