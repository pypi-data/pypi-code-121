import os
from typing import Optional

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.client.openapi_client.models.create_experimental_workspace import (
    CreateExperimentalWorkspace,
)
from anyscale.controllers.cluster_controller import ClusterController
from anyscale.controllers.project_controller import ProjectController
from anyscale.controllers.workspace_controller import WorkspaceController


ANYSCALE_WORKSPACES_SSH_OPTIONS = [
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "IdentitiesOnly=yes",
]


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
    _do_pull(pull_git_state=True)


@workspace_cli.command(name="pull", help="Pull files from a workspace on Anyscale.")
@click.option(
    "--pull-git-state",
    required=False,
    is_flag=True,
    default=False,
    help="Also pull git state. This will add additional overhead.",
)
def pull(pull_git_state) -> None:
    _do_pull(pull_git_state)


@workspace_cli.command(name="push", help="Push files to a workspace on Anyscale.")
@click.option(
    "--push-git-state",
    required=False,
    is_flag=True,
    default=False,
    help="Also push git state. This is currently unoptimized and will be very slow.",
)
def push(push_git_state) -> None:
    _do_push(push_git_state)


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
    "--no-push",
    "-s",
    required=False,
    is_flag=True,
    default=False,
    help="Whether to skip pushing files prior to running the command.",
)
def run(command: str, as_job: bool, no_push: bool,) -> None:
    if as_job:
        raise NotImplementedError("Running as a job isn't implemented yet.")
    workspace_controller = WorkspaceController()
    # Generally, we assume the user wants to run their command in the context of
    # their latest file changes.
    if not no_push:
        _do_push(push_git_state=False)
    workspace_controller.run_cmd(
        ANYSCALE_WORKSPACES_SSH_OPTIONS, f"cd ~/workspace-project-* && {command}",
    )


def _do_pull(pull_git_state):
    workspace_controller = WorkspaceController()
    # Since workspaces store git objects in an EFS alternates dir, we have to force
    # a repack prior to pulling. Otherwise, the pulled git repo may not be fully
    # functional locally. A repack is expensive, but we assume pulls aren't frequent.
    if pull_git_state:
        workspace_controller.run_cmd(
            ANYSCALE_WORKSPACES_SSH_OPTIONS,
            "cd ~/workspace-project-* && git repack -a -d",
        )
    workspace_controller.run_rsync(
        ANYSCALE_WORKSPACES_SSH_OPTIONS,
        workspace_controller.project_definition.root,
        down=True,
        rsync_filters=[".gitignore"],
        rsync_excludes=[".anyscale.yaml"] + ([] if pull_git_state else [".git"]),
    )


def _do_push(push_git_state):
    workspace_controller = WorkspaceController()
    workspace_controller.run_rsync(
        ANYSCALE_WORKSPACES_SSH_OPTIONS,
        workspace_controller.project_definition.root,
        down=False,
        rsync_filters=[".gitignore"],
        # TODO(ekl) to efficiently push the git state, we need to do this in two
        # phases: first sync the shared git objects to EFS, then sync non .git files.
        # Otherwise this will be very slow since our local git representation is
        # different from the remote one (has large .pack files).
        rsync_excludes=[".anyscale.yaml"] + ([] if push_git_state else [".git"]),
    )
