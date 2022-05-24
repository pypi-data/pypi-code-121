from abc import ABC, abstractmethod
from datetime import datetime
import os
from pathlib import Path
import time
from typing import Any, cast, Dict, List, Optional, Tuple, Type, Union
from urllib.parse import urlparse

import click
from pydantic import BaseModel, Field, root_validator
import requests
from requests.adapters import HTTPAdapter
import tabulate
from urllib3 import Retry
import yaml

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client import (
    CreateProductionJob,
    DecoratedProductionJob,
    HaJobStates,
    JobsLogsQueryInfo,
    ProductionJobConfig,
)
from anyscale.cluster_compute import (
    get_cluster_compute_from_name,
    get_default_cluster_compute,
)
from anyscale.cluster_env import (
    get_build_from_cluster_env_identifier,
    get_default_cluster_env_build,
    validate_successful_build,
)
from anyscale.controllers.base_controller import BaseController
from anyscale.project import (
    find_project_root,
    get_proj_id_from_name,
    get_project_id,
    ProjectDefinition,
)
from anyscale.util import get_endpoint, PROJECT_NAME_ENV_VAR
from anyscale.utils.runtime_env import upload_and_rewrite_working_dir


log = BlockLogger()


def _validate_conda_option(conda_option: Union[str, Dict]) -> Union[str, Dict]:
    """Parses and validates a user-provided 'conda' option.

    Can be one of three cases:
        1) A str that's the name of a pre-installed conda environment.
        2) A string pointing to a local conda environment YAML. In this case,
           the file contents will be read into a dict.
        3) A dict that defines a conda environment. This is passed through.
    """
    result = None
    if isinstance(conda_option, str):
        yaml_file = Path(conda_option)
        if yaml_file.suffix in (".yaml", ".yml"):
            if not yaml_file.is_file():
                raise click.ClickException(f"Can't find conda YAML file {yaml_file}.")
            try:
                result = yaml.safe_load(yaml_file.read_text())
            except Exception as e:
                raise click.ClickException(
                    f"Failed to read conda file {yaml_file}: {e}."
                )
        else:
            # Assume it's a pre-existing conda environment name.
            result = conda_option
    elif isinstance(conda_option, dict):
        result = conda_option

    return result


def _validate_pip_option(pip_option: Union[str, List[str]]) -> Optional[List[str]]:
    """Parses and validates a user-provided 'pip' option.

    Can be one of two cases:
        1) A List[str] describing the requirements. This is passed through.
        2) A string pointing to a local requirements file. In this case, the
           file contents will be read split into a list.
    """
    result = None
    if isinstance(pip_option, str):
        # We have been given a path to a requirements.txt file.
        pip_file = Path(pip_option)
        if not pip_file.is_file():
            raise click.ClickException(f"{pip_file} is not a valid file.")
        result = pip_file.read_text().strip().split("\n")
    elif isinstance(pip_option, list) and all(
        isinstance(dep, str) for dep in pip_option
    ):
        if len(pip_option) == 0:
            result = None
        else:
            result = pip_option

    return result


def _validate_py_modules(py_modules_option: List[str]) -> List[str]:
    for entry in py_modules_option:
        if "://" not in entry:
            raise click.ClickException(
                "Only remote URIs are currently supported for py_modules in the job "
                "config (not local directories). Please see "
                "https://docs.ray.io/en/master/handling-dependencies.html#remote-uris for supported options."
            )

    return py_modules_option


def _working_dir_is_remote_uri(working_dir: str) -> bool:
    return "://" in working_dir


def _validate_working_dir(working_dir_option: str) -> str:
    """If working_dir is a local directory, check that it exists."""
    if not _working_dir_is_remote_uri(working_dir_option):
        # We have been given a path to a local directory.
        if not Path(working_dir_option).is_dir():
            raise click.ClickException(
                f"working_dir {working_dir_option} is not a valid local directory or remote URI."
            )

    return working_dir_option


def _validate_working_dir_and_upload_path(
    working_dir: Optional[str], upload_path: Optional[str]
):
    """Check that the combination of working_dir and upload_path is valid.

    The rule is that working_dir is a local directory if and only if upload_path is specified.
    """
    if upload_path is not None:
        if working_dir is None or _working_dir_is_remote_uri(working_dir):
            raise click.ClickException(
                f"`upload_path` was specified, but `working_dir` is not a local directory.  Received `upload_path`: {upload_path} and `working_dir`: {working_dir}."
            )
    else:
        if working_dir is not None and not _working_dir_is_remote_uri(working_dir):
            raise click.ClickException(
                f"{working_dir} is a local directory, but `upload_path` was not specified in the runtime_env. Please specify a remote URI in `upload_path`, e.g. `s3://my_bucket/my_dir`."
            )


def _validate_upload_path(upload_path: str) -> str:
    """Check that the upload path is a valid S3 or GS remote URI."""
    try:
        parsed_upload_path = urlparse(upload_path)
    except Exception as e:
        raise click.ClickException(
            f"Failed to parse `upload_path` {upload_path} as a URI (e.g. 's3://my_bucket/my_dir'): {e}"
        )
    if parsed_upload_path.scheme not in ["s3", "gs"]:
        raise click.ClickException(
            f"Only Amazon S3 (e.g. 's3://bucket', 's3://bucket/path') and Google Storage URIs (e.g. 'gs://bucket', 'gs://bucket/path') are supported. Received {upload_path}."
        )
    return upload_path


def _validate_env_vars(env_vars: Dict[str, str]) -> Dict[str, str]:
    for key, value in env_vars.items():
        if not isinstance(key, str):
            raise click.ClickException(
                f"env_vars key {key} is not a string. Please check the formatting."
            )
        if not isinstance(value, str):
            raise click.ClickException(
                f"env_vars value {value} is not a string. Please check the formatting."
            )

    return env_vars


class JobConfig(BaseModel):
    """
    Job Config model for CLI. Validate and preprocess so `entrypoint`, `runtime_env_config`,
    `build_id`, `compute_config_id`, `max_retries` have the correct values to call
    `/api/v2/decorated_ha_jobs/create`.
    """

    entrypoint: str = Field(
        ...,
        description="A script that will be run to start your job. This command will be run in the root directory of the specified runtime env. Eg. 'python script.py'",
    )
    name: Optional[str] = Field(
        None,
        description="Name of job to be submitted. Default will be used if not provided.",
    )
    description: Optional[str] = Field(
        None,
        description="Description of job to be submitted. Default will be used if not provided.",
    )
    runtime_env: Optional[Dict[str, Any]] = Field(
        None,
        description="A ray runtime env json. Your entrypoint will be run in the environment specified by this runtime env.",
    )
    build_id: Optional[str] = Field(
        None,
        description="The id of the cluster env build. This id will determine the docker image your job is run on.",
    )
    cluster_env: Optional[str] = Field(
        None,
        description="The name of the cluster environment and build revision in format `my_cluster_env:1`.",
    )
    compute_config_id: Optional[str] = Field(
        None,
        description="The id of the compute configuration that you want to use. This id will specify the resources required for your job",
    )
    project_id: Optional[str] = Field(
        None,
        description="The id of the project you want to use. If not specified, and no project is inferred from the directory, no project will be used.",
    )
    project: Optional[str] = Field(
        None,
        description="The name of the project you want to use. If not specified, and no project is inferred from the directory, no project will be used.",
    )
    compute_config: Optional[str] = Field(
        None,
        description="The name of the compute configuration that you want to use. This will specify the resources required for your job",
    )
    cloud: Optional[str] = Field(
        None,
        description="The cloud name to specify a default compute configuration with. This will specify the resources required for your job",
    )
    max_retries: Optional[int] = Field(
        5,
        description="The number of retries this job will attempt on failure. Set to None to set infinite retries",
    )

    @root_validator
    def fill_project_id(cls: Any, values: Any) -> Any:  # noqa: N805
        project_id, project_name = (
            values.get("project_id"),
            values.get("project"),
        )
        if project_id and project_name:
            raise click.ClickException(
                "Only one of `project_id` or `project` can be provided in the job config file. "
            )
        project_name_env_var = os.environ.get(PROJECT_NAME_ENV_VAR)
        if project_name_env_var:
            # Get project from environment variable regardless of if is provided in config
            values["project_id"] = get_proj_id_from_name(project_name_env_var)
        elif project_name:
            values["project_id"] = get_proj_id_from_name(project_name)
        return values

    @root_validator
    def fill_build_id(cls: Any, values: Any) -> Any:  # noqa: N805
        build_id, cluster_env = (
            values.get("build_id"),
            values.get("cluster_env"),
        )
        if cluster_env and build_id:
            raise click.ClickException(
                "Only one of `cluster_env` or `build_id` can be provided in the job config file. "
            )
        if cluster_env:
            build_id = get_build_from_cluster_env_identifier(cluster_env).id
            values["build_id"] = build_id
        elif not build_id:
            log.info(
                "No cluster environment provided, setting default based on local Python and Ray versions."
            )
            build_id = get_default_cluster_env_build().id
            values["build_id"] = build_id
        validate_successful_build(values["build_id"])
        return values

    @root_validator
    def fill_compute_config_id(cls: Any, values: Any) -> Any:  # noqa: N805
        compute_config_id, compute_config, cloud = (
            values.get("compute_config_id"),
            values.get("compute_config"),
            values.get("cloud"),
        )
        if bool(compute_config_id) + bool(compute_config) + bool(cloud) > 1:
            raise click.ClickException(
                "Only one of `compute_config_id`, `compute_config`, or `cloud` can be provided in the job config file."
            )
        if compute_config:
            compute_config_id = get_cluster_compute_from_name(compute_config).id
            values["compute_config_id"] = compute_config_id
        elif cloud:
            # Get default cluster compute for the specified cloud.
            compute_config_id = get_default_cluster_compute(cloud, None).id
            values["compute_config_id"] = compute_config_id
            log.info(
                f"Using default compute config for specified cloud {cloud}: {compute_config_id}."
            )
        elif not compute_config_id:
            # Get default cluster compute for the default cloud.
            compute_config_id = get_default_cluster_compute(None, None).id
            values["compute_config_id"] = compute_config_id
            log.info(
                f"No cloud or compute config specified, using the default: {compute_config_id}."
            )

        return values

    @root_validator
    def validate_runtime_env(cls: Any, values: Any) -> Any:  # noqa: N805
        runtime_env = values.get("runtime_env")
        if runtime_env is not None:
            if "conda" in runtime_env:
                conda_option = runtime_env["conda"]
                if not isinstance(conda_option, (str, dict)):
                    raise click.ClickException(
                        f"runtime_env['conda'] must be str or dict, got type({conda_option})."
                    )
                runtime_env["conda"] = _validate_conda_option(conda_option)
            if "pip" in runtime_env:
                pip_option = runtime_env["pip"]
                if not isinstance(pip_option, (str, list)):
                    raise click.ClickException(
                        f"runtime_env['pip'] must be str or list, got type({pip_option})."
                    )
                runtime_env["pip"] = _validate_pip_option(runtime_env["pip"])
            if "py_modules" in runtime_env:
                py_modules_option = runtime_env["py_modules"]
                if not isinstance(py_modules_option, list):
                    raise click.ClickException(
                        f"runtime_env['py_modules'] must be list, got type({py_modules_option})."
                    )
                runtime_env["py_modules"] = _validate_py_modules(py_modules_option)
            if "upload_path" in runtime_env:
                upload_path_option = runtime_env["upload_path"]
                if not isinstance(upload_path_option, str):
                    raise click.ClickException(
                        f"runtime_env['upload_path'] must be str, got type({upload_path_option})."
                    )
                runtime_env["upload_path"] = _validate_upload_path(upload_path_option)
            if "working_dir" in runtime_env:
                working_dir_option = runtime_env["working_dir"]
                if not isinstance(working_dir_option, str):
                    raise click.ClickException(
                        f"runtime_env['working_dir'] must be str, got type({working_dir_option})."
                    )
                runtime_env["working_dir"] = _validate_working_dir(working_dir_option)
            _validate_working_dir_and_upload_path(
                runtime_env.get("working_dir"), runtime_env.get("upload_path")
            )
            if "env_vars" in runtime_env:
                env_vars_option = runtime_env["env_vars"]
                if not isinstance(env_vars_option, dict):
                    raise click.ClickException(
                        f"runtime_env['env_vars'] must be dict, got type({env_vars_option})."
                    )
                runtime_env["env_vars"] = _validate_env_vars(env_vars_option)
            values["runtime_env"] = runtime_env

        return values


class LogProvider(ABC):
    @abstractmethod
    def __init__(self, dns_name: str, anyscale_token: str, query: str) -> None:
        pass

    @abstractmethod
    def query(
        self, start_timestamp_ns: int, end_timestamp_ns: int
    ) -> List[Tuple[int, str]]:
        """Query logs for a time range, return list of (timestamp_ns, log_line)."""


class LokiLogProvider(LogProvider):
    def __init__(self, dns_name: str, anyscale_token: str, query: str) -> None:
        # https://grafana.com/docs/loki/latest/api/#get-lokiapiv1query_range
        self.url = f"https://{dns_name}/loki/api/v1/query_range"
        self.params: Dict[str, Union[str, int]] = {
            "token": anyscale_token,
            "query": query,
            "limit": 1000,
            "start": 0,
            "end": int(time.time() * 1e9),
            "direction": "forward",
        }

        self.session = requests.Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=10, backoff_factor=0.1, allowed_methods=["GET"])
            ),
        )

    def query(
        self, start_timestamp_ns: int, end_timestamp_ns: int
    ) -> List[Tuple[int, str]]:
        self.params["start"] = start_timestamp_ns
        self.params["end"] = end_timestamp_ns

        resp = self.session.get(self.url, params=self.params)
        resp.raise_for_status()

        resp_data = resp.json()
        if resp_data["status"] != "success":
            raise click.ClickException("Querying Anyscale log endpoint failed.")
        if resp_data["data"]["resultType"] != "streams":
            raise click.ClickException("Invalid metrics type.")

        lines = []
        for log_chunk in resp_data["data"]["result"]:
            # TODO(simon): potentially annotate the log with the log_chunk["stream"] metadata
            for timestamp, line in log_chunk["values"]:
                lines.append((int(timestamp), line))

        return lines


class JobController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.log.open_block("Output")

    def submit(
        self, job_config_file: str, name: Optional[str], description: Optional[str]
    ) -> None:
        job_config = self._read_job_config(job_config_file)
        project_id = job_config.project_id

        # If project id is not specified, try to infer it
        if not project_id:
            # Check directory of .anyscale.yaml to decide whether to use default project.
            root_dir = find_project_root(os.getcwd())
            if root_dir is not None:
                project_definition = ProjectDefinition(root_dir)
                project_id = get_project_id(project_definition.root)
                project_name = self.anyscale_api_client.get_project(
                    project_id
                ).result.name
                self.log.warning(
                    ".anyscale.yaml has been detected in this project directory. The functionality of "
                    "using this file to select the project has been deprecated, and will be removed "
                    f"in April 2022. Please instead specify `project_id: {project_id}` in the job config file. "
                    "The project name can also be specified by setting the environment variable "
                    f'`{PROJECT_NAME_ENV_VAR}="{project_name}"`.'
                )
            else:
                default_project = self.anyscale_api_client.get_default_project().result
                project_id = default_project.id
                self.log.info("No project specified. Continuing without a project.")
        if job_config.runtime_env:
            job_config.runtime_env = upload_and_rewrite_working_dir(
                job_config.runtime_env, self.log
            )

        config_object = ProductionJobConfig(
            entrypoint=job_config.entrypoint,
            runtime_env=job_config.runtime_env,
            build_id=job_config.build_id,
            compute_config_id=job_config.compute_config_id,
            max_retries=job_config.max_retries,
        )

        job = self.api_client.create_job_api_v2_decorated_ha_jobs_create_post(
            CreateProductionJob(
                name=name
                or job_config.name
                or "cli-job-{}".format(datetime.now().isoformat()),
                description=description
                or job_config.description
                or "Job submitted from CLI",
                project_id=project_id,
                config=config_object,
            )
        ).result

        self.log.info(
            f"Job {job.id} has been successfully submitted. Current state of job: {job.state.current_state}."
        )
        self.log.info(
            f"Query the status of the job with `anyscale job list --job-id {job.id}`."
        )
        self.log.info(
            f"Get the logs for the job with `anyscale job logs --job-id {job.id} --follow`."
        )
        self.log.info(f'View the job in the UI at {get_endpoint(f"/jobs/{job.id}")}.')

    def _read_job_config(self, job_config_file: str) -> JobConfig:
        if not os.path.exists(job_config_file):
            raise click.ClickException(f"Config file {job_config_file} not found.")

        with open(job_config_file, "r") as f:
            config_dict = yaml.safe_load(f)

        job_config = JobConfig.parse_obj(config_dict)
        return job_config

    def list(
        self,
        include_all_users: bool,
        name: Optional[str],
        job_id: Optional[str],
        project_id: Optional[str],
        max_items: int,
        is_service: bool = False,
    ) -> None:
        """
        This function will either list jobs or services based on the value of `is_service`.
        Both functionalities are combined in one function because the API to list both these
        entities is currently the same.
        """
        entity_type = "services" if is_service else "jobs"
        print(f'View your {entity_type} in the UI at {get_endpoint(f"/{entity_type}")}')

        jobs_list = []
        if job_id:
            job = self.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get(
                job_id
            ).result
            if not is_service and job.is_service:
                # `job_id` belongs to a service, but this function should list jobs.
                raise click.ClickException(
                    f"ID {job_id} belongs to a Anyscale service. Please get information about "
                    f"this service with `anyscale service list --service-id {job_id}`."
                )
            elif is_service and not job.is_service:
                # `job_id` belongs to a job, but this function should list services.
                raise click.ClickException(
                    f"ID {job_id} belongs to a Anyscale job. Please get information about "
                    f"this job with `anyscale job list --job-id {job_id}`."
                )
            output_map = {
                "Name": job.name,
                "Id": job.id,
                "Cost (dollars)": job.cost_dollars,
                "Project name": job.project.name,
                "Cluster name": job.last_job_run.cluster.name
                if job.last_job_run and job.last_job_run.cluster
                else None,
                "Current state": job.state.current_state,
                "Creator": job.creator.username,
                "Entrypoint": job.config.entrypoint
                if len(job.config.entrypoint) < 100
                else job.config.entrypoint[:100] + " ...",
            }
            if is_service:
                output_map["Access"] = job.access
                output_map["URL"] = job.url
                output_map["Token"] = job.token

            output_str = "\n".join(
                [f"\t{key}: {output_map[key]}" for key in output_map]
            )
            print(output_str)
            return
        else:
            if not include_all_users:
                creator_id = (
                    self.api_client.get_user_info_api_v2_userinfo_get().result.id
                )
            else:
                creator_id = None
            resp = self.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get(
                project_id=project_id,
                name=name,
                creator_id=creator_id,
                type_filter="SERVICE" if is_service else "BATCH_JOB",
                count=10,
            )
            jobs_list.extend(resp.results)
            paging_token = resp.metadata.next_paging_token
            has_more = (paging_token is not None) and (len(jobs_list) < max_items)
            while has_more:
                resp = self.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get(
                    project_id=project_id,
                    name=name,
                    creator_id=creator_id,
                    type_filter="SERVICE" if is_service else "BATCH_JOB",
                    count=10,
                    paging_token=paging_token,
                )
                jobs_list.extend(resp.results)
                paging_token = resp.metadata.next_paging_token
                has_more = (paging_token is not None) and (len(jobs_list) < max_items)
            jobs_list = jobs_list[:max_items]

        jobs_table = [
            [
                job.name,
                job.id,
                job.cost_dollars,
                job.project.name,
                job.last_job_run.cluster.name
                if job.last_job_run and job.last_job_run.cluster
                else None,
                job.state.current_state,
                job.creator.username,
                job.config.entrypoint
                if len(job.config.entrypoint) < 50
                else job.config.entrypoint[:50] + " ...",
            ]
            for job in jobs_list
        ]

        table = tabulate.tabulate(
            jobs_table,
            headers=[
                "NAME",
                "ID",
                "COST",
                "PROJECT NAME",
                "CLUSTER NAME",
                "CURRENT STATE",
                "CREATOR",
                "ENTRYPOINT",
            ],
            tablefmt="plain",
        )
        print(f"{entity_type.capitalize()}:\n{table}")

    def terminate(
        self, job_id: Optional[str], job_name: Optional[str], is_service: bool = False,
    ) -> None:
        """
        This function will either terminate jobs or services based on the value of `is_service`.
        Both functionalities are combined in one function because the API to terminate both these
        entities is currently the same.
        """
        entity_type = "service" if is_service else "job"
        job_resp: DecoratedProductionJob = self._resolve_job_object(
            job_id, job_name, entity_type
        )
        job = self.api_client.terminate_job_api_v2_decorated_ha_jobs_production_job_id_terminate_post(
            job_resp.id
        ).result
        self.log.info(f"{entity_type.capitalize()} {job.id} has begun terminating...")
        self.log.info(
            f" Current state of {entity_type}: {job.state.current_state}. Goal state of {entity_type}: {job.state.goal_state}"
        )
        self.log.info(
            f"Query the status of the {entity_type} with `anyscale {entity_type} list --{entity_type}-id {job.id}`."
        )

    def _resolve_job_object(
        self, job_id: Optional[str], job_name: Optional[str], entity_type: str = "job"
    ) -> DecoratedProductionJob:
        """Given job_id or job_name, retrieve decorated ha job spec"""
        if job_id is None and job_name is None:
            raise click.ClickException(
                f"Either `--id` or `--name` must be passed in for {entity_type}."
            )
        if job_id is None:
            jobs_resp = self.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get(
                name=job_name,
                type_filter="BATCH_JOB" if entity_type == "job" else "SERVICE",
            ).results
            if len(jobs_resp) == 0:
                raise click.ClickException(
                    f"No {entity_type} found with name {job_name}. Please either pass `--id` or list the "
                    f"available {entity_type}s with `anyscale {entity_type} list`."
                )
            if len(jobs_resp) > 1:
                raise click.ClickException(
                    f"Multiple {entity_type}s found with name {job_name}. Please specify the `--id` instead."
                )
            job_id = jobs_resp[0].id
        jobs_resp = self.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get(
            production_job_id=job_id
        ).result
        return jobs_resp

    def _wait_for_a_job_run(self, job_id: str) -> str:
        """Given job_id, wait until there is a job run on a cluster."""
        last_job_run_id = None
        terminal_state = {
            HaJobStates.SUCCESS,
            HaJobStates.TERMINATED,
            HaJobStates.BROKEN,
            HaJobStates.OUT_OF_RETRIES,
        }
        while last_job_run_id is None:
            job_object = self.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get(
                production_job_id=job_id
            ).result
            job_state = job_object.state.current_state
            last_job_run_id = job_object.last_job_run_id
            if job_state in terminal_state and last_job_run_id is None:
                raise click.ClickException(
                    f"Can't find latest job run for {job_state} job."
                )
            if last_job_run_id is None:
                self.log.info(f"Waiting for a job run, current state is {job_state}.")
                time.sleep(5)
        return last_job_run_id

    def logs(
        self,
        job_id: Optional[str],
        job_name: Optional[str],
        should_follow: bool = False,
        log_provider_cls: Type[LogProvider] = LokiLogProvider,
    ) -> None:
        job_id = self._resolve_job_object(job_id, job_name).id
        self._wait_for_a_job_run(cast(str, job_id))

        # TODO(simon): implement ability to look through logs from previous tries
        log_info: JobsLogsQueryInfo = self.api_client.get_job_logs_query_info_api_v2_decorated_ha_jobs_production_job_id_logs_query_get(
            production_job_id=job_id
        ).result

        log_provider = log_provider_cls(
            dns_name=log_info.loki_dns_name,
            anyscale_token=log_info.access_token,
            query=log_info.loki_query,
        )

        start_timestamp_ns = 0
        end_timestamp_ns = int(time.time() * 1e9)
        while True:
            lines = log_provider.query(start_timestamp_ns, end_timestamp_ns)

            for time_stamp, line in lines:
                # Update the start timestamp in case we are following or paginated.
                start_timestamp_ns = time_stamp
                print(line)

            # No log entry for our time range.
            if len(lines) == 0:
                if should_follow:
                    # Avoid repeatedly polling empty log entry. Sleep here to give loki server a break.
                    time.sleep(1)
                else:
                    break

            # Update the params for updated range.
            start_timestamp_ns += 1  # Start time should exclude the previous entries.
            if should_follow:  # end time should only be updated when we are following.
                end_timestamp_ns = int(time.time() * 1e9)
