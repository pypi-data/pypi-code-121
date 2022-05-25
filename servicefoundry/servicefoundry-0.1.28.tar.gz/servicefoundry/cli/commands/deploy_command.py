import logging
from threading import Thread

import rich_click as click

from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.internal.build import LOCAL, REMOTE, build_and_deploy
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)

logger = logging.getLogger(__name__)


@click.command(name="deploy", cls=COMMAND_CLS, help="Deploy servicefoundry Service")
@click.option("--local", is_flag=True, default=False)
@click.option("--env", "-e", type=click.STRING)
@click.argument("service_dir", type=click.Path(exists=True), nargs=1, default="./")
@handle_exception_wrapper
def deploy(local, env, service_dir):
    build = LOCAL if local else REMOTE
    # @TODO Give ability to user confirmation.
    # @TODO Pick servicefoundry.{env}.yaml based on env
    deployment = build_and_deploy(
        base_dir=service_dir,
        build=build,
        callback=RichOutputCallBack(),
    )
    if isinstance(deployment, Thread):
        deployment.join()
    else:
        # print_obj("Deployment", deployment)
        if not CliConfig.get("json"):
            # tail logs
            tfs_client = ServiceFoundryServiceClient.get_client()
            tfs_client.tail_logs(deployment["runId"], wait=True)


def get_deploy_command():
    return deploy
