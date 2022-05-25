import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from vessl import list_ssh_keys
from vessl.cli._base import VesslGroup, vessl_argument, vessl_option
from vessl.cli._util import (
    Endpoint,
    generic_prompter,
    print_data,
    print_logs,
    print_table,
    prompt_choices,
    truncate_datetime,
)
from vessl.cli.experiment import (
    cpu_limit_option,
    dataset_option,
    gpu_limit_option,
    gpu_type_option,
    image_url_option,
    memory_limit_option,
    processor_type_option,
    root_volume_size_option,
    upload_local_file_option,
)
from vessl.cli.kernel_cluster import cluster_option
from vessl.cli.kernel_resource_spec import resource_option
from vessl.cli.organization import organization_name_option
from vessl.util.common import safe_cast
from vessl.util.constant import SSH_CONFIG_PATH
from vessl.workspace import (
    backup_workspace,
    connect_workspace_ssh,
    create_workspace,
    list_workspace_logs,
    list_workspaces,
    read_workspace,
    restore_workspace,
    start_workspace,
    stop_workspace,
    terminate_workspace,
    update_vscode_remote_ssh,
)


class WorkspacePortType(click.ParamType):
    name = "Port type"

    def convert(self, raw_value: Any, param, ctx) -> Any:
        tokens = raw_value.split()

        if len(tokens) < 3:
            raise click.BadOptionUsage(
                option_name="port",
                message=f"Invalid value for [PORT]: '{raw_value}' must be of form [expose_type] [port] [name].",
            )

        port_num = safe_cast(tokens[1], to_type=int)
        if port_num is None:
            raise click.BadOptionUsage(
                option_name="port",
                message=f"Invalid value for [PORT]: 'port' must be a number.",
            )

        port = {"expose_type": tokens[0], "port": port_num, "name": tokens[2]}
        return port


def ssh_private_key_path_callback(
    ctx: click.Context, param: click.Parameter, key_path: str
) -> Optional[str]:
    if key_path:
        return key_path

    ssh_keys = list_ssh_keys()
    if len(ssh_keys) == 0:
        raise click.BadParameter(
            "At least one ssh public key should be added.\n"
            "Please run `vessl ssh-key add`."
        )

    for ssh_key in ssh_keys:
        key_path = os.path.join(Path.home(), ".ssh", ssh_key.filename.rstrip(".pub"))
        if os.path.exists(key_path):
            return key_path

    for key_path in (
        os.path.join(Path.home(), ".ssh", "id_rsa"),
        os.path.join(Path.home(), ".ssh", "id_ed25519"),
    ):
        if os.path.exists(key_path):
            return key_path

    return None


def workspace_id_prompter(
    ctx: click.Context, param: click.Parameter, value: int
) -> int:
    workspaces = list_workspaces()
    if len(workspaces) == 0:
        raise click.UsageError("No valid workspaces.")
    return prompt_choices("Workspace", [(x.name, x.id) for x in workspaces])


def start_workspace_id_prompter(
    ctx: click.Context, param: click.Parameter, value: int
) -> int:
    workspaces = list_workspaces(statuses=["stopped"])
    if len(workspaces) == 0:
        raise click.UsageError("No valid workspaces.")
    return prompt_choices("Workspace", [(x.name, x.id) for x in workspaces])


def stop_workspace_id_prompter(
    ctx: click.Context, param: click.Parameter, value: int
) -> int:
    workspaces = list_workspaces(
        statuses=["queued", "pending", "initializing", "running"]
    )
    if len(workspaces) == 0:
        raise click.UsageError("No valid workspaces.")
    return prompt_choices("Workspace", [(x.name, x.id) for x in workspaces])


@click.command(name="workspace", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@organization_name_option
def list():
    workspaces = list_workspaces()
    print_table(
        workspaces,
        ["ID", "Name", "Status", "Created", "Creator", "Cluster", "Resource"],
        lambda x: [
            x.id,
            x.name,
            x.status,
            truncate_datetime(x.created_dt),
            x.created_by.username,
            x.kernel_cluster.name,
            x.kernel_resource_spec.name,
        ],
    )


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=workspace_id_prompter,
)
@organization_name_option
def read(id: int):
    workspace = read_workspace(workspace_id=id)
    print_data(
        {
            "ID": workspace.id,
            "Name": workspace.name,
            "Status": workspace.status,
            "Created": truncate_datetime(workspace.created_dt),
            "Creator": workspace.created_by.username,
            "Cluster": workspace.kernel_cluster.name,
            "Image": workspace.kernel_image.name,
            "Resource": workspace.kernel_resource_spec.name,
        }
    )
    print(
        f"For more info: {Endpoint.workspace.format(workspace.organization.name, workspace.id)}"
    )


@cli.vessl_command()
@vessl_argument("name", type=click.STRING, prompter=generic_prompter("Name"))
@cluster_option
@vessl_option(
    "--node",
    type=click.STRING,
    multiple=True,
    help="Cluster nodes. Defaults to all nodes in cluster.",
)
@resource_option
@processor_type_option
@cpu_limit_option
@memory_limit_option
@gpu_type_option
@gpu_limit_option
@image_url_option
@vessl_option(
    "--max-hours",
    type=click.INT,
    default=24,
    help="Maximum number of hours to run workspace. Defaults to 24.",
)
@dataset_option
@upload_local_file_option
@root_volume_size_option
@vessl_option(
    "-p",
    "--port",
    type=WorkspacePortType(),
    multiple=True,
    help="Format: [expose_type] [port] [name], ex. `-p 'tcp 22 ssh'`. Jupyter and SSH ports exist by default.",
)
@vessl_option("--init-script", type=click.STRING, help="Custom init script")
@organization_name_option
def create(
    name: str,
    cluster: str,
    node: List[str],
    resource: str,
    processor_type: str,
    cpu_limit: float,
    memory_limit: str,
    gpu_type: str,
    gpu_limit: int,
    image_url: str,
    max_hours: int,
    dataset: List[str],
    upload_local_file: List[str],
    root_volume_size: str,
    port: List[Dict[str, Any]],
    init_script: str,
):
    workspace = create_workspace(
        name=name,
        cluster_name=cluster,
        cluster_node_names=node,
        kernel_resource_spec_name=resource,
        processor_type=processor_type,
        cpu_limit=cpu_limit,
        memory_limit=memory_limit,
        gpu_type=gpu_type,
        gpu_limit=gpu_limit,
        kernel_image_url=image_url,
        max_hours=max_hours,
        dataset_mounts=dataset,
        local_files=upload_local_file,
        root_volume_size=root_volume_size,
        ports=port,
        init_script=init_script,
    )
    print(
        f"Created '{workspace.name}'.\n"
        f"For more info: {Endpoint.workspace.format(workspace.organization.name, workspace.id)}"
    )


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=workspace_id_prompter,
)
@click.option(
    "--tail",
    type=click.INT,
    default=200,
    help="Number of lines to display (from the end).",
)
@organization_name_option
def logs(id: int, tail: int):
    logs = list_workspace_logs(workspace_id=id, tail=tail)
    print_logs(logs)


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=start_workspace_id_prompter,
)
@organization_name_option
def start(id: int):
    workspace = start_workspace(workspace_id=id)
    print(
        f"Started '{workspace.name}'.\n"
        f"For more info: {Endpoint.workspace.format(workspace.organization.name, workspace.id)}"
    )


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=stop_workspace_id_prompter,
)
@organization_name_option
def stop(id: int):
    workspace = stop_workspace(workspace_id=id)
    print(
        f"Stopped '{workspace.name}'.\n"
        f"For more info: {Endpoint.workspace.format(workspace.organization.name, workspace.id)}"
    )


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=workspace_id_prompter,
)
@organization_name_option
def terminate(id: int):
    workspace = terminate_workspace(workspace_id=id)
    print(
        f"Terminated '{workspace.name}'.\n"
        f"For more info: {Endpoint.workspace.format(workspace.organization.name, workspace.id)}"
    )


@cli.vessl_command()
@vessl_option(
    "-p",
    "--key-path",
    type=click.Path(exists=True),
    callback=ssh_private_key_path_callback,
    help="Path to SSH private key.",
)
@organization_name_option
def ssh(key_path: str):
    connect_workspace_ssh(private_key_path=key_path)


@cli.vessl_command()
@vessl_option(
    "-p",
    "--key-path",
    type=click.STRING,
    callback=ssh_private_key_path_callback,
    help="SSH private key path.",
)
@organization_name_option
def vscode(key_path: str):
    update_vscode_remote_ssh(private_key_path=key_path)
    print(f"Updated '{SSH_CONFIG_PATH}'.")


@cli.vessl_command()
@organization_name_option
def backup():
    backup_workspace()


@cli.vessl_command()
@organization_name_option
def restore():
    restore_workspace()
