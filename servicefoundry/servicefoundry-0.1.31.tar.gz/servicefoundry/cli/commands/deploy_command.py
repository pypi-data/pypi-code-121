import logging

import rich_click as click

from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.deploy.deploy import deploy, deploy_local
from servicefoundry.internal.package.package import package

logger = logging.getLogger(__name__)

LOCAL = "local"
REMOTE = "remote"


def _deploy(local):
    callback = RichOutputCallBack()
    packaged_output = package(callback=callback)
    if local:
        local_process = deploy_local(packaged_output, callback=callback)
        local_process.join()
    else:
        deployment = deploy(packaged_output)
        if not CliConfig.get("json"):
            tfs_client = ServiceFoundryServiceClient.get_client()
            tfs_client.tail_logs(deployment["runId"], wait=True)


@click.group(name="deploy", cls=GROUP_CLS, invoke_without_command=True)
@click.option("--local", is_flag=True, default=False)
@click.pass_context
@handle_exception_wrapper
def deploy_command(ctx, local):
    if ctx.invoked_subcommand is None:
        _deploy(local)


@click.command(name="inference", cls=COMMAND_CLS, help="Create a new Cluster")
@click.option("--local", is_flag=True, default=False)
@handle_exception_wrapper
def inference_command(local):
    print("Invoked")
    _deploy(local)


def get_deploy_command():
    deploy_command.add_command(inference_command)
    return deploy_command
