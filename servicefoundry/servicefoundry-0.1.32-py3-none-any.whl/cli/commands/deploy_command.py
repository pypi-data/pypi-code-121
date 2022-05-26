import logging

import rich_click as click

import servicefoundry.core as sfy
from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from servicefoundry.cli.io.cli_input_hook import CliInputHook
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


@click.command(name="function", cls=COMMAND_CLS, help="Deploy a python function.")
@click.option("--python_service_file", type=click.STRING, default=None)
@click.option("--service_name", type=click.STRING, default=None)
@click.option("--workspace", type=click.STRING, default=None)
@click.option("--python_version", type=click.STRING, default=None)
@click.option("--local", is_flag=True, default=False)
@handle_exception_wrapper
def function_command(
    python_service_file, service_name, workspace, python_version, local
):
    _component_command(
        sfy.Service, python_service_file, service_name, workspace, python_version, local
    )


@click.command(name="webapp", cls=COMMAND_CLS, help="Deploy a python function.")
@click.option("--python_service_file", type=click.STRING, default=None)
@click.option("--service_name", type=click.STRING, default=None)
@click.option("--workspace", type=click.STRING, default=None)
@click.option("--python_version", type=click.STRING, default=None)
@click.option("--local", is_flag=True, default=False)
@handle_exception_wrapper
def webapp_command(python_service_file, service_name, workspace, python_version, local):
    _component_command(
        sfy.Webapp, python_service_file, service_name, workspace, python_version, local
    )


def _component_command(
    cls, python_service_file, service_name, workspace, python_version, local
):
    parameters = {}
    if python_service_file:
        parameters["python_service_file"] = python_service_file
    if service_name:
        parameters["service_name"] = service_name
    if workspace:
        parameters["workspace"] = workspace
    if python_version:
        parameters["python_version"] = python_version

    tfs_client = ServiceFoundryServiceClient.get_client()
    component = cls(parameters, input_hook=CliInputHook(tfs_client))
    if local:
        component.deploy_local()
    else:
        component.deploy()


def get_deploy_command():
    deploy_command.add_command(function_command)
    deploy_command.add_command(webapp_command)
    return deploy_command
