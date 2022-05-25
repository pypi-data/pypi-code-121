import os
import platform
import sys
from typing import List

import psutil
import pynvml

from openapi_client import DistributedExperimentCreateAPIInput
from openapi_client.models import (
    ExperimentCreateAPIInput,
    InfluxdbWorkloadLog,
    LocalExperimentCreateAPIInput,
    OrmHyperparameter,
    ResponseExperimentInfo,
    ResponseExperimentListResponse,
    StorageFile,
    ResponseGitHubCodeRef,
)
from openapi_client.models.orm_execution_environment import OrmExecutionEnvironment
from vessl import __version__, vessl_api
from vessl.kernel_cluster import read_cluster
from vessl.kernel_resource_spec import (
    _configure_custom_kernel_resource_spec,
    read_kernel_resource_spec,
)
from vessl.organization import _get_organization_name
from vessl.project import _get_project_name
from vessl.util import logger
from vessl.util.common import safe_cast
from vessl.util.constant import MOUNT_PATH_OUTPUT, SOURCE_TYPE_OUTPUT
from vessl.util.exception import (
    InvalidExperimentError,
    InvalidParamsError,
    VesslApiException,
)
from vessl.volume import (
    _configure_volume_mount_requests,
    copy_volume_file,
    list_volume_files,
)


def read_experiment(
    experiment_number: int,
    **kwargs,
) -> ResponseExperimentInfo:
    """Read experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): experiment number.

    Example:
        ```python
        vessl.read_experiment(
            experiment_number=23,
        )
        ```
    """
    return vessl_api.experiment_read_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )


def read_experiment_by_id(experiment_id: int) -> ResponseExperimentInfo:
    result = vessl_api.experiment_read_by_idapi(experiment_id=experiment_id)
    assert isinstance(result, ResponseExperimentInfo)
    return result


def list_experiments(
    statuses: List[str] = None,
    **kwargs,
) -> List[ResponseExperimentListResponse]:
    """List experiments in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        statuses(List[str]): A list of status filter. Defaults to None.

    Example:
        ```python
        vessl.list_experiments(
            statuses=["completed"]
        )
        ```
    """
    statuses = (
        [",".join(statuses)] if statuses else None
    )  # since openapi-generator uses repeating params instead of commas
    return vessl_api.experiment_list_api(
        statuses=statuses,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    ).results


def create_experiment(
    cluster_name: str,
    start_command: str,
    kernel_resource_spec_name: str = None,
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: str = None,
    gpu_type: str = None,
    gpu_limit: int = None,
    kernel_image_url: str = None,
    *,
    message: str = None,
    termination_protection: bool = False,
    hyperparameters: List[str] = None,
    dataset_mounts: List[str] = None,
    model_mounts: List[str] = None,
    git_ref_mounts: List[str] = None,
    git_diff_mount: str = None,
    local_files: List[str] = None,
    upload_local_git_diff: bool = False,
    archive_file_mount: str = None,
    root_volume_size: str = None,
    working_dir: str = None,
    output_dir: str = MOUNT_PATH_OUTPUT,
    worker_count: int = 1,
    framework_type: str = None,
    **kwargs,
) -> ResponseExperimentInfo:
    """Create experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`. You can also configure git info by passing
    `git_branch` or `git_ref` as `**kwargs`. Pass `use_git_diff=True` if
    you want to run experiment with uncommitted changes and pass
    `use_git_diff_untracked=True` if you want to run untracked changes(only
    valid if `use_git_diff` is set).

    Args:
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
        message(str): Message. Defaults to None.
        termination_protection(bool): True if termination protection is enabled,
            False otherwise. Defaults to False.
        hyperparameters(List[str]): A list of hyperparameters. Defaults to None.
        dataset_mounts(List[str]): A list of dataset mounts. Defaults to None.
        model_mounts(List[str]): A list of model mounts. Defaults to None.
        git_ref_mounts(List[str]): A list of git repository mounts. Defaults to
            None.
        git_diff_mount(str): Git diff mounts. Defaults to None.
        local_files(List[str]): A list of local files to upload. Defaults to
            None.
        upload_local_git_diff(bool): True if local git diff to upload, False
            otherwise. Defaults to False.
        archive_file_mount(str): Local archive file mounts. Defaults to None.
        root_volume_size(str): Root volume size. Defaults to None.
        working_dir(str): Working directory path. Defaults to None.
        output_dir(str): Output directory path. Defaults to "/output/".
        worker_count(int): Number of workers(for distributed experiment only).
            Defaults to 1.
        framework_type(str): Specify "pytorch" or "tensorflow" (for distributed
            experiment only). Defaults to None.

    Example:
        ```python
        vessl.create_experiment(
            cluster_name="aws-apne2-prod1",
            kernel_resource_spec_name="v1.cpu-4.mem-13",
            kernel_image_url="public.ecr.aws/vessl/kernels:py36.full-cpu",
            dataset_mounts=["/input/:mnist"]
            start_command="pip install requirements.txt && python main.py",
        )
        ```
    """
    cluster = read_cluster(cluster_name)

    kernel_resource_spec = kernel_resource_spec_id = None
    if kernel_resource_spec_name:
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

    volume_mount_requests = _configure_volume_mount_requests(
        dataset_mounts=dataset_mounts,
        git_ref_mounts=git_ref_mounts,
        git_diff_mount=git_diff_mount,
        archive_file_mount=archive_file_mount,
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        output_dir=output_dir,
        model_mounts=model_mounts,
        local_files=local_files,
        upload_local_git_diff=upload_local_git_diff,
        **kwargs,
    )
    if worker_count > 1:
        return vessl_api.distributed_experiment_create_api(
            organization_name=_get_organization_name(**kwargs),
            project_name=_get_project_name(**kwargs),
            distributed_experiment_create_api_input=DistributedExperimentCreateAPIInput(
                cluster_id=cluster.id,
                hyperparameters=[
                    OrmHyperparameter(key, str(value))
                    for key, value in map(
                        lambda hyperparameter: hyperparameter.split("="),
                        (hyperparameters or []),
                    )
                ],
                framework_type=framework_type,
                image_url=kernel_image_url,
                message=message,
                worker_replicas=worker_count,
                worker_resource_spec=kernel_resource_spec,
                worker_resource_spec_id=kernel_resource_spec_id,
                start_command=start_command,
                termination_protection=termination_protection,
                volumes=volume_mount_requests,
            ),
        )

    return vessl_api.experiment_create_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        experiment_create_api_input=ExperimentCreateAPIInput(
            cluster_id=cluster.id,
            hyperparameters=[
                OrmHyperparameter(key, str(value))
                for key, value in map(
                    lambda hyperparameter: hyperparameter.split("="),
                    (hyperparameters or []),
                )
            ],
            image_url=kernel_image_url,
            message=message,
            resource_spec=kernel_resource_spec,
            resource_spec_id=kernel_resource_spec_id,
            start_command=start_command,
            termination_protection=termination_protection,
            volumes=volume_mount_requests,
        ),
    )


def _create_orm_execution_environment():
    cpu_count = psutil.cpu_count()

    gpu_count = gpu_type = None
    try:
        pynvml.nvmlInit()
        gpu_count = pynvml.nvmlDeviceGetCount()
        gpu_type = pynvml.nvmlDeviceGetName(
            pynvml.nvmlDeviceGetHandleByIndex(0)
        ).decode("utf8")
    except pynvml.nvml.NVMLError:
        pass

    hostname = platform.node()
    os = platform.platform(aliased=True)
    python_version = platform.python_version()
    python_executable = sys.executable
    start_command = " ".join(sys.argv)
    vessl_version = __version__

    return OrmExecutionEnvironment(
        cpu_count=cpu_count,
        gpu_count=gpu_count,
        gpu_type=gpu_type,
        hostname=hostname,
        os=os,
        python_version=python_version,
        python_executable=python_executable,
        start_command=start_command,
        vessl_version=vessl_version,
    )


def create_local_experiment(
    message: str = None, hyperparameters: dict = None, **kwargs
):
    return vessl_api.local_experiment_create_api(
        local_experiment_create_api_input=LocalExperimentCreateAPIInput(
            execution_environment=_create_orm_execution_environment(),
            message=message,
            hyperparameters=hyperparameters,
        ),
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )


def list_experiment_logs(
    experiment_number: int,
    tail: int = 200,
    worker_number: int = 0,
    after: int = 0,
    **kwargs,
) -> List[InfluxdbWorkloadLog]:
    """List experiment logs in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_name (int): Experiment number.
        tail (int): The number of lines to display from the end. Display all if
            -1. Defaults to 200.
        worker_number (int): Override default worker number (for distributed
            experiments only). Defaults to 0.
        after (int): The number of starting lines to display from the start.
            Defaults to 0.

    Example:
        ```python
        vessl.list_experiment_logs(
            experiment_number=23,
        )
        ```
    """
    if tail == -1:
        tail = None

    experiment = read_experiment(experiment_number, **kwargs)

    if experiment.is_distributed:
        str_worker_number = safe_cast(worker_number, str, "0")
        return vessl_api.distributed_experiment_logs_api(
            experiment_number=experiment_number,
            limit=tail,
            organization_name=_get_organization_name(**kwargs),
            project_name=_get_project_name(**kwargs),
            distributed_number=worker_number,
        ).logs[str_worker_number]

    return vessl_api.experiment_logs_api(
        experiment_number=experiment_number,
        limit=tail,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        after=after,
    ).logs


def list_experiment_output_files(
    experiment_number: int,
    need_download_url: bool = False,
    recursive: bool = True,
    worker_number: int = 0,
    **kwargs,
) -> List[StorageFile]:
    """List experiment output files in the default organization/project. If you
    want to override the default organization/project, then pass
    `organization_name` or `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.
        need_download_url(bool): True if you need a download URL, False
            otherwise. Defaults to False.
        recursive(bool): True if list files recursively, False otherwise.
            Defaults to True.
        worker_number(int): Override default worker number (for distributed
            experiments only). Defaults to 0.

    Example:
        ```python
        vessl.list_experiment_output_files(
            experiment_number=23,
        )
        ```
    """
    experiment = read_experiment(experiment_number, **kwargs)

    if experiment.is_local:
        volume_id = experiment.local_execution_spec.output_volume_id
        return list_volume_files(
            volume_id=volume_id,
            need_download_url=need_download_url,
            path="",
            recursive=recursive,
        )

    if experiment.is_distributed:
        worker_replicas = experiment.distributed_spec.pytorch_spec.worker_replicas
        if worker_number >= worker_replicas:
            raise InvalidParamsError(
                "worker-number: should be less than {}".format(worker_replicas)
            )

        mounts = experiment.volume_mounts_list[worker_number].mounts
    else:
        mounts = experiment.volume_mounts.mounts

    for volume_mount in mounts:
        if volume_mount.source_type == SOURCE_TYPE_OUTPUT:
            base_path = volume_mount.volume.sub_path
            try:
                files = list_volume_files(
                    volume_id=volume_mount.volume.volume_id,
                    need_download_url=need_download_url,
                    path=base_path,
                    recursive=recursive,
                )
            except VesslApiException:
                files = []
            for file in files:
                file.path = os.path.relpath(f"/{file.path}", base_path)
            return files

    logger.info("No output volume mounted")


def download_experiment_output_files(
    experiment_number: int,
    dest_path: str = os.path.join(os.getcwd(), "output"),
    worker_number: int = 0,
    **kwargs,
) -> None:
    """Download experiment output files in the default organization/project.
    If you want to override the default organization/project, then pass
    `organization_name` or `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.
        dest_path(str): Local download path. Defaults to "./output".
        worker_number(int): Override default worker number (for distributed
            experiments only). Defaults to 0.

    Example:
        ```python
        vessl.download_experiment_output_files(
            experiment_number=23,
        )
        ```
    """
    experiment = read_experiment(experiment_number, **kwargs)

    if experiment.is_local:
        volume_id = experiment.local_execution_spec.output_volume_id
        return copy_volume_file(
            source_volume_id=volume_id,
            source_path="",
            dest_volume_id=None,
            dest_path=dest_path,
        )
    if experiment.is_distributed:
        worker_replicas = experiment.distributed_spec.pytorch_spec.worker_replicas
        if worker_number >= worker_replicas:
            raise InvalidParamsError(
                "worker-number: should be less than {}".format(worker_replicas)
            )

        for volume_mount in experiment.volume_mounts_list[worker_number].mounts:
            if volume_mount.source_type == SOURCE_TYPE_OUTPUT:
                return copy_volume_file(
                    source_volume_id=volume_mount.volume.volume_id,
                    source_path="",
                    dest_volume_id=None,
                    dest_path=dest_path,
                )
    else:
        for volume_mount in experiment.volume_mounts.mounts:
            if volume_mount.source_type == SOURCE_TYPE_OUTPUT:
                return copy_volume_file(
                    source_volume_id=volume_mount.volume.volume_id,
                    source_path="",
                    dest_volume_id=None,
                    dest_path=dest_path,
                )

    logger.info("No output volume mounted")


def upload_experiment_output_files(experiment_number: int, path: str, **kwargs):
    """Upload experiment output files in the default organization/project.
    If you want to override the default organization/project, then pass
    `organization_name` or `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.
        path(str): Source path.

    Example:
        ```python
        vessl.upload_experiment_output_files(
            experiment_number=23,
            path="output",
        )
        ```
    """
    experiment = read_experiment(experiment_number, **kwargs)
    if not experiment.is_local:
        raise InvalidExperimentError("Experiment cannot be VESSL-managed.")

    return copy_volume_file(
        source_volume_id=None,
        source_path=path,
        dest_volume_id=experiment.local_execution_spec.output_volume_id,
        dest_path="",
    )


def terminate_experiment(
    experiment_number: int, **kwargs
) -> ResponseExperimentInfo:
    """Terminate experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.

    Example:
        ```python
        vessl.terminate_experiment(
            experiment_number=23,
        )
        ```
    """
    return vessl_api.experiment_terminate_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )


def list_github_code_refs(workload_id: int) -> List[ResponseGitHubCodeRef]:
    return vessl_api.experiment_git_hub_code_refs_api(
        workload_id=workload_id,
    ).results


def delete_experiment(experiment_number: int, **kwargs):
    """Delete experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.

    Example:
        ```python
        vessl.delete_experiment(
            experiment_number=23,
        )
        ```
    """
    return vessl_api.experiment_delete_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )
