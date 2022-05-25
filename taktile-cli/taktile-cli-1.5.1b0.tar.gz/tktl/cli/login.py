import typing as t

import click

from tktl.commands import login as login_commands
from tktl.core.exceptions import APIClientException
from tktl.core.loggers import LOG
from tktl.login import login as tktl_login


@click.command("login", help="Log in & store api key")
@click.argument("api_key", required=False)
def login(api_key: t.Optional[str]):

    if not api_key:
        api_key = click.prompt("Please enter your API key", hide_input=True)

    if tktl_login(api_key=api_key):
        command = login_commands.LogInCommand()
        try:
            command.execute()
        except APIClientException as e:
            LOG.error(f"Authentication failed: {e}")


@click.command("logout", help="Log out & remove apiKey from config file")
def logout():
    command = login_commands.LogOutCommand()
    command.execute()
