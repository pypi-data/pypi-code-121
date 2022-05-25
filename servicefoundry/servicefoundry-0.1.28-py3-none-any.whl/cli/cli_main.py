import rich_click as click

from servicefoundry import __version__
from servicefoundry.cli.commands import (
    get_create_command,
    get_delete_command,
    get_deploy_command,
    get_get_command,
    get_init_command,
    get_list_command,
    get_login_command,
    get_logout_command,
    get_set_command,
)
from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import GROUP_CLS
from servicefoundry.cli.util import setup_rich_click


def create_service_foundry_cli():
    """Generates CLI by combining all subcommands into a main CLI and returns in

    Returns:
        function: main CLI functions will all added sub-commands
    """
    _cli = service_foundry_cli
    _cli.add_command(get_init_command())
    _cli.add_command(get_deploy_command())
    _cli.add_command(get_login_command())
    _cli.add_command(get_get_command())
    _cli.add_command(get_list_command())
    _cli.add_command(get_delete_command())
    _cli.add_command(get_create_command())
    _cli.add_command(get_logout_command())
    _cli.add_command(get_set_command())
    return _cli


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    cls=GROUP_CLS, context_settings=CONTEXT_SETTINGS, invoke_without_command=True
)
@click.option("--json", is_flag=True)
@click.option("--logs", is_flag=True)
@click.version_option(__version__)
@click.pass_context
def service_foundry_cli(ctx, json, logs):
    """
    Servicefoundry provides an easy way to deploy your code as a web service.
    \b

    To start, login to your Truefoundry account with `sfy login`

    \b
    Once logged in, start a new service with `sfy init`
    """
    setup_rich_click()
    # TODO (chiragjn): Change this to -o json|yaml|table|pager
    CliConfig.set("json", json)
    CliConfig.set("logs", logs)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
