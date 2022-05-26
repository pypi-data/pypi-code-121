import logging

import rich_click as click

from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import (
    COMMAND_CLS,
    ENABLE_CLUSTER_COMMANDS,
    ENABLE_SECRETS_COMMANDS,
    GROUP_CLS,
)
from servicefoundry.cli.display_util import print_obj
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.lib import workspace as workspace_lib

logger = logging.getLogger(__name__)

WORKSPACE_DISPLAY_FIELDS = [
    "id",
    "name",
    "namespace",
    "status",
    "clusterId",
    "createdBy",
    "createdAt",
    "updatedAt",
]
DEPLOYMENT_DISPLAY_FIELDS = [
    "id",
    "serviceId",
    "domain",
    "deployedBy",
    "createdAt",
    "updatedAt",
]


@click.group(name="create", cls=GROUP_CLS)
def create_command():
    # TODO (chiragjn): Figure out a way to update supported resources based on ENABLE_* flags
    """
    Create servicefoundry resources

    \b
    Supported resources:
    - Workspace
    """
    pass


@click.command(name="cluster", cls=COMMAND_CLS, help="Create a new Cluster")
@click.argument("name")
@click.argument("region")
@click.argument("aws_account_id")
@click.argument("server_name")
@click.argument("ca_data")
@click.argument("server_url")
@handle_exception_wrapper
def create_cluster(name, region, aws_account_id, server_name, ca_data, server_url):
    tfs_client = ServiceFoundryServiceClient.get_client()
    cluster = tfs_client.create_cluster(
        name, region, aws_account_id, server_name, ca_data, server_url
    )
    print_obj("Cluster", cluster)


@click.command(name="workspace", cls=COMMAND_CLS, help="Create a new Workspace")
@click.argument("name", type=click.STRING)
@click.option(
    "-c",
    "--cluster",
    type=click.STRING,
    default=None,
    help="cluster to create this workspace in",
)
@click.option("--non-interactive", is_flag=True, default=False)
@handle_exception_wrapper
def create_workspace(name, cluster, non_interactive):
    tail_logs = not CliConfig.get("json")
    workspace = workspace_lib.create_workspace(
        name=name,
        cluster_name_or_id=cluster,
        non_interactive=non_interactive,
        tail_logs=tail_logs,
    )
    print_obj("Workspace", workspace.to_dict())


@click.command(name="secret-group", cls=COMMAND_CLS, help="Create a new Secret Group")
@click.argument("secret_group_name")
@handle_exception_wrapper
def create_secret_group(secret_group_name):
    tfs_client = ServiceFoundryServiceClient.get_client()
    response = tfs_client.create_secret_group(secret_group_name)
    print_obj(f"Secret Group", response)


@click.command(name="secret", cls=COMMAND_CLS, help="Create a new Secret")
@click.argument("secret_group_id")
@click.argument("secret_key")
@click.argument("secret_value")
@handle_exception_wrapper
def create_secret(secret_group_id, secret_key, secret_value):
    tfs_client = ServiceFoundryServiceClient.get_client()
    response = tfs_client.create_secret(secret_group_id, secret_key, secret_value)
    print_obj(response["id"], response)


def get_create_command():
    create_command.add_command(create_workspace)

    if ENABLE_CLUSTER_COMMANDS:
        create_command.add_command(create_cluster)

    if ENABLE_SECRETS_COMMANDS:
        create_command.add_command(create_secret)
        create_command.add_command(create_secret_group)

    return create_command
