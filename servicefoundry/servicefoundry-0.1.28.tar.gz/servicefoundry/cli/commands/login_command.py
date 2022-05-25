import logging

import rich_click as click

from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.internal import lib
from servicefoundry.internal.console import console
from servicefoundry.internal.lib.messages import PROMPT_POST_LOGIN

logger = logging.getLogger(__name__)


@click.command(name="login", cls=COMMAND_CLS)
@handle_exception_wrapper
def login():
    """
    Login to servicefoundry

    \b
    Once logged in, you can initiate a new service with `sfy init`
    and deploy the service with `sfy deploy .`
    """
    # TODO (chiragjn): Add support for non interactive login with API key.
    #                  It is supported indirectly as we always look for `SERVICE_FOUNDRY_API_KEY`
    #                  in the environment
    lib.login(interactive=True)
    console.print(PROMPT_POST_LOGIN)


def get_login_command():
    return login
