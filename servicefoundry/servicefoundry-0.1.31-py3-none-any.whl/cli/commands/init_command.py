import logging
import os
from types import SimpleNamespace

import questionary
import rich_click as click
from questionary import Choice

from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.io.cli_input_hook import CliInputHook
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.internal import lib
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.console import console
from servicefoundry.internal.const import SERVICE_DEF_FILE_NAME
from servicefoundry.internal.exceptions import ConfigurationException
from servicefoundry.internal.session_factory import get_session
from servicefoundry.internal.template.template_workflow import TemplateWorkflow
from servicefoundry.internal.util import BadRequestException

logger = logging.getLogger(__name__)


@click.command(
    name="init", cls=COMMAND_CLS, help="Initialize a new Service for servicefoundry"
)
@handle_exception_wrapper
def init():
    # Get SFSClient
    tfs_client = ServiceFoundryServiceClient.get_client()

    # is_current = questionary.confirm(
    #     "Do you want to create project in current directory?"
    # ).ask()
    # if is_current:
    #     if (
    #         os.path.isfile(SERVICE_DEF_FILE_NAME)
    #         and not questionary.confirm(
    #             "Do you want to overwrite existing servicefoundry.yaml?"
    #         ).ask()
    #     ):
    #         console.print("Aborted init")
    #         return

    # Static call to get list of templates
    templates = tfs_client.list_template()
    input_hook = CliInputHook(tfs_client)

    # Choose a template of service to be created.
    template_choices = [
        Choice(f'{t["id"]} - {t["description"]}', value=t["id"]) for t in templates
    ]
    template_id = questionary.select("Choose a template", template_choices).ask()
    template_workflow = TemplateWorkflow(
        f"truefoundry.com/v1/{template_id}", input_hook
    )

    # if is_current:
    #     parameters["service_name"] = os.path.split(os.getcwd())[1]
    template_workflow.process_parameter()

    out_folder = ""
    # if not is_current:
    if "service_name" in template_workflow.parameters:
        out_folder = template_workflow.parameters.get("service_name")
    else:
        raise ConfigurationException("Service was not provided")

    if os.path.exists(out_folder):
        raise ConfigurationException(f"Folder {out_folder} already exist.")

    print(f"Setting output folder to {out_folder}")

    template_workflow.write(out_folder=out_folder, input_hook=input_hook)

    # @TODO This should be taken care inside template workflow
    if template_workflow.template.post_init_instruction:
        console.print(
            template_workflow.template.post_init_instruction.format(
                parameters=SimpleNamespace(**template_workflow.parameters)
            )
        )


def get_init_command():
    return init
