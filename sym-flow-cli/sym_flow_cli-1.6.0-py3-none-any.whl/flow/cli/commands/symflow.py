import os

import click
from sym.shared.cli.decorators import setup_segment, setup_sentry
from sym.shared.cli.helpers.sym_group import SymGroup
from sym.shared.cli.helpers.updater import SymUpdater

from sym.flow.cli.commands.bots import bots_commands
from sym.flow.cli.commands.config import config_commands
from sym.flow.cli.commands.debug import debug_commands
from sym.flow.cli.commands.login import login, logout
from sym.flow.cli.commands.policies import policies_commands
from sym.flow.cli.commands.resources import resources_commands
from sym.flow.cli.commands.services import services_commands
from sym.flow.cli.commands.status import status
from sym.flow.cli.commands.tokens import tokens_commands
from sym.flow.cli.commands.update import update
from sym.flow.cli.commands.users import users_commands
from sym.flow.cli.commands.version import version
from sym.flow.cli.helpers.constants import (
    DEFAULT_API_URL,
    DEFAULT_AUTH_URL,
    SegmentWriteKey,
    SentryDSN,
)

from ..helpers.global_options import GlobalOptions
from ..version import __version__


@click.group(
    name="symflow", cls=SymGroup, context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option(
    "--debug", is_flag=True, help="enable verbose debugging", envvar="SYM_DEBUG"
)
@click.option(
    "--api-url",
    default=DEFAULT_API_URL,
    help="set the Sym API URL",
    envvar="SYM_API_URL",
)
@click.option(
    "--auth-url",
    default=DEFAULT_AUTH_URL,
    help="set the Sym auth url",
    envvar="SYM_AUTH_URL",
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
@setup_segment(write_key=SegmentWriteKey)
@setup_sentry(dsn=SentryDSN, release=f"sym-flow-cli@{__version__}")
def symflow(options: GlobalOptions, auth_url: str, api_url: str, debug: bool) -> None:
    """
    Manage Sym Services and Users in your organization

    https://docs.symops.com/docs/using-the-symflow-cli
    """

    options.debug = debug
    if sym_jwt := os.getenv("SYM_JWT"):
        options.set_access_token(sym_jwt)
    options.set_api_url(api_url)
    options.set_auth_url(auth_url)
    options.dprint(auth_url=auth_url, api_url=api_url)

    SymUpdater(debug=debug).auto_update()


symflow.add_command(version)
symflow.add_command(update)
symflow.add_command(login)
symflow.add_command(logout)
symflow.add_command(status)
symflow.add_command(services_commands)
symflow.add_command(users_commands)
symflow.add_command(debug_commands)
symflow.add_command(config_commands)
symflow.add_command(policies_commands)
symflow.add_command(tokens_commands)
symflow.add_command(bots_commands)
symflow.add_command(resources_commands)
