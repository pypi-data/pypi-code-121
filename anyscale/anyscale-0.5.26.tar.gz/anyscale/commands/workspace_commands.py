import os
from typing import Optional

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.client.openapi_client.models.create_experimental_workspace import (
    CreateExperimentalWorkspace,
)
from anyscale.controllers.cluster_controller import ClusterController
from anyscale.controllers.project_controller import ProjectController
from anyscale.controllers.session_controller import SessionController


@click.group("workspace", help="Interact with workspaces on Anyscale.", hidden=True)
def workspace_cli() -> None:
    pass


@workspace_cli.command(name="create", help="Create a workspace on Anyscale.")
@click.option(
    "--name", "-n", required=True, help="Name of the workspace to create.",
)
@click.option("--cloud-id", required=True)
@click.option("--cluster-env-build-id", required=True)
@click.option("--compute-config-id", required=True)
def create(
    name: str, cloud_id: str, cluster_env_build_id: str, compute_config_id: str,
) -> None:
    auth_api_client = get_auth_api_client()
    api_client = auth_api_client.api_client
    api_client.create_workspace_api_v2_experimental_workspaces_post(
        CreateExperimentalWorkspace(
            name=name,
            cloud_id=cloud_id,
            compute_config_id=compute_config_id,
            cluster_environment_build_id=cluster_env_build_id,
        )
    )


@workspace_cli.command(name="start", help="Start an existing workspace on Anyscale.")
@click.option(
    "--name",
    "-n",
    required=True,
    default=None,
    help="Name of existing workspace to start.",
)
def start(name: Optional[str],) -> None:
    cluster_controller = ClusterController()
    # TODO(ekl) query the workspace cluster name from the DB.
    cluster_controller.start(
        cluster_name=f"workspace-cluster-{name}",
        cluster_id=None,
        cluster_env_name=None,
        docker=None,
        python_version=None,
        ray_version=None,
        cluster_compute_name=None,
        cluster_compute_file=None,
        cloud_name=None,
        idle_timeout=None,
        project_id=None,
        project_name=None,
        user_service_access=None,
    )


@workspace_cli.command(name="terminate", help="Terminate a workspace on Anyscale.")
@click.option(
    "--name",
    "-n",
    required=True,
    default=None,
    help="Name of existing workspace to terminate.",
)
def terminate(name: Optional[str],) -> None:
    cluster_controller = ClusterController()
    cluster_controller.terminate(
        cluster_name=f"workspace-cluster-{name}",
        cluster_id=None,
        project_id=None,
        project_name=None,
    )


@workspace_cli.command(name="clone", help="Clone a workspace on Anyscale.")
@click.option(
    "--name",
    "-n",
    required=True,
    default=None,
    help="Name of existing workspace to clone.",
)
def clone(name: Optional[str],) -> None:
    project_controller = ProjectController()
    project_controller.clone(f"workspace-project-{name}", owner=None)
    os.chdir(f"workspace-project-{name}")
    _do_pull()


@workspace_cli.command(name="pull", help="Pull files from a workspace on Anyscale.")
def pull() -> None:
    _do_pull()


@workspace_cli.command(name="push", help="Push files to a workspace on Anyscale.")
def push() -> None:
    _do_push()


@workspace_cli.command(
    name="run", help="Run a command in a workspace, syncing files first if needed."
)
@click.argument("command", required=True)
@click.option(
    "--as-job",
    "-j",
    required=False,
    is_flag=True,
    default=False,
    help="Run the command as a background job in a new cluster.",
)
@click.option(
    "--no-sync",
    "-s",
    required=False,
    is_flag=True,
    default=False,
    help="Whether to skip pushing files prior to running the command.",
)
def run(command: str, as_job: bool, no_sync: bool,) -> None:
    if as_job:
        raise NotImplementedError("Running as a job isn't implemented yet.")
    # Generally, we assume the user wants to run their command in the context of
    # their latest file changes.
    if not no_sync:
        _do_push()
    _run_cmd(command)


def _do_pull():
    # Since workspaces store git objects in an EFS alternates dir, we have to force
    # a repack prior to pulling. Otherwise, the pulled git repo may not be fully
    # functional locally. A repack is expensive, but we assume pulls aren't frequent.
    _run_cmd("git repack -a -d")
    session_controller = SessionController()
    session_controller.pull(
        session_name=None,
        source=None,
        target=None,
        config=None,
        # Always sync everything, including the .git state.
        rsync_exclude_override=[],
    )


def _run_cmd(cmd):
    session_controller = SessionController()
    session_controller.ssh(
        "",
        ssh_option=[],
        worker_node_id=None,
        worker_node_ip=None,
        force_head_node=False,
        project_id=None,
        cmd=f"cd ~/workspace-project-* && {cmd}",
    )


def _do_push():
    session_controller = SessionController()
    session_controller.push(
        session_name=None,
        source=None,
        target=None,
        config=None,
        all_nodes=False,
        # Always sync everything, including the .git state.
        rsync_exclude_override=[],
    )
