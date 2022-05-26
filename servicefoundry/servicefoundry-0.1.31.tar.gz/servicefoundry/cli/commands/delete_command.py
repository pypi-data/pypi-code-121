import logging

import rich_click as click
from rich import print_json

from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import (
    COMMAND_CLS,
    ENABLE_AUTHORIZE_COMMANDS,
    ENABLE_CLUSTER_COMMANDS,
    ENABLE_SECRETS_COMMANDS,
    GROUP_CLS,
)
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.lib import service as service_lib
from servicefoundry.internal.lib import workspace as workspace_lib

logger = logging.getLogger(__name__)


@click.group(name="delete", cls=GROUP_CLS)
def delete_command():
    # TODO (chiragjn): Figure out a way to update supported resources based on ENABLE_* flags
    """
    Servicefoundry delete resource

    \b
    Supported resources:
    - Workspace
    - Service
    """
    pass


@click.command(name="cluster", cls=COMMAND_CLS, help="Delete a Cluster")
@click.argument("cluster_id")
@click.confirmation_option(prompt="Are you sure you want to delete this cluster?")
@handle_exception_wrapper
def delete_cluster(cluster_id):
    tfs_client = ServiceFoundryServiceClient.get_client()
    tfs_client.delete_cluster(cluster_id)
    # delete workspace and cluster from context
    ctx_cluster = tfs_client.session.get_cluster()
    if ctx_cluster and ctx_cluster["id"] == cluster_id:
        tfs_client.session.set_workspace(None)
        tfs_client.session.set_cluster(None)
        tfs_client.session.save_session()


@click.command(name="workspace", cls=COMMAND_CLS, help="Delete a Workspace")
@click.argument("name", type=click.STRING)
@click.option(
    "-c",
    "--cluster",
    type=click.STRING,
    default=None,
    help="cluster to delete the workspace from",
)
@click.confirmation_option(prompt="Are you sure you want to delete this workspace?")
@handle_exception_wrapper
def delete_workspace(name, cluster):
    # Tests:
    # - Set Context -> delete workspace -> Should give error to give workspace name
    # - Set Context -> delete workspace valid_name -> Should delete
    # - Set Context -> delete workspace invalid_name -> Should give error no such workspace in set cluster
    # - Set Context -> delete workspace name -c 'invalid_cluster_name' -> Should give error invalid cluster
    # - Set Context -> delete workspace invalid_name -c 'cluster_name' -> Should give error invalid workspace
    # - Set Context -> delete workspace valid_name -c 'cluster_name' -> Should delete
    # - No Context -> delete workspace -> Should give error to give workspace name
    # - No Context -> delete workspace valid_name -> Try to resolve, if only one exists then delete
    #                 otherwise error to give cluster
    # - No Context -> delete workspace invalid_name -> Tries to resolve, if only one exists then delete
    #                 otherwise error to give cluster
    # - No Context -> delete workspace name -c 'invalid_cluster_name' -> Should give error invalid cluster
    # - No Context -> delete workspace invalid_name -c 'cluster_name' -> Should give error invalid workspace
    # - No Context -> delete workspace valid_name -c 'cluster_name' -> Should delete
    tail_logs = not CliConfig.get("json")
    response = workspace_lib.delete_workspace(
        name_or_id=name,
        cluster_name_or_id=cluster,
        tail_logs=tail_logs,
        non_interactive=True,
    )
    if not tail_logs:
        print_json(data=response)


@click.command(
    name="service",
    cls=COMMAND_CLS,
    help="Delete a deployed Service and its deployments",
)
@click.argument("name", type=click.STRING)
@click.option(
    "-w",
    "--workspace",
    type=click.STRING,
    default=None,
    help="workspace to find this service in",
)
@click.option(
    "-c",
    "--cluster",
    type=click.STRING,
    default=None,
    help="cluster to find this cluster in",
)
@click.confirmation_option(prompt="Are you sure you want to delete this service?")
@handle_exception_wrapper
def delete_service(name, workspace, cluster):
    tail_logs = not CliConfig.get("json")
    response = service_lib.delete_service(
        name_or_id=name,
        workspace_name_or_id=workspace,
        cluster_name_or_id=cluster,
        tail_logs=tail_logs,
        non_interactive=True,
    )
    if not tail_logs:
        print_json(data=response)


@click.command(name="secret-group", cls=COMMAND_CLS, help="Delete a Secret Group")
@click.argument("secret_group_id")
@click.confirmation_option(prompt="Are you sure you want to delete this secret group?")
@handle_exception_wrapper
def delete_secret_group(secret_group_id):
    tfs_client = ServiceFoundryServiceClient.get_client()
    response = tfs_client.delete_secret_group(secret_group_id)
    print_json(data=response)


@click.command(name="secret", cls=COMMAND_CLS, help="Delete a Secret")
@click.argument("secret_id")
@click.confirmation_option(prompt="Are you sure you want to delete this secret?")
@handle_exception_wrapper
def delete_secret(secret_id):
    tfs_client = ServiceFoundryServiceClient.get_client()
    response = tfs_client.delete_secret(secret_id)
    print_json(data=response)


@click.command(name="auth", cls=COMMAND_CLS, help="Delete authorization")
@click.argument("authorization_id")
@click.confirmation_option(prompt="Are you sure you want to delete this authorization?")
@handle_exception_wrapper
def delete_auth(authorization_id):
    tfs_client = ServiceFoundryServiceClient.get_client()
    response = tfs_client.delete_authorization(authorization_id)
    print_json(data=response)


def get_delete_command():
    delete_command.add_command(delete_workspace)
    delete_command.add_command(delete_service)

    if ENABLE_AUTHORIZE_COMMANDS:
        delete_command.add_command(delete_auth)

    if ENABLE_CLUSTER_COMMANDS:
        delete_command.add_command(delete_cluster)

    if ENABLE_SECRETS_COMMANDS:
        delete_command.add_command(delete_secret)
        delete_command.add_command(delete_secret_group)

    return delete_command
