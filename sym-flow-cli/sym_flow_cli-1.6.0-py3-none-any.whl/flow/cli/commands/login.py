import sys

import click
import requests
import validators

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.config import Config, store_login_config
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.login.login_flow import LoginFlow


def validate_email(ctx, param, value):
    """Returns value if the email address is valid, raises otherwise."""
    if value and not validators.email(value):
        raise click.BadParameter("must enter a valid email address")
    return value


@click.command(short_help="Log in to your Sym account")
@click.make_pass_decorator(GlobalOptions, ensure=True)
@click.option(
    "--browser/--no-browser",
    default=True,
    is_flag=True,
)
@click.option(
    "--port",
    default=11001,
)
@click.option(
    "--email",
    callback=validate_email,
    prompt=True,
    default=lambda: Config.get_email() if Config.is_logged_in() else None,
)
def login(options: GlobalOptions, browser: bool, port: int, email: str) -> None:
    """Log in to your Sym account to authenticate with the Sym API. This is required to enable privileged actions within your Organization such as authoring Sym Flows or installing the Slack App.

    \b
    Example:
        `symflow login --email user@symops.io`
    """
    if options.access_token:
        click.secho("SYM_JWT is set, unset SYM_JWT to login as a regular user", fg="red")
        sys.exit(1)

    org = options.sym_api.get_organization_from_email(email)
    if options.debug:
        click.echo("Org: {slug} ({client_id})\n".format(**org))
    else:
        click.echo("Org: {slug}\n".format(**org))

    flow = LoginFlow.get_login_flow(email, browser, port)

    if browser:
        (url, *_) = flow.gen_browser_login_params(options, org)
        styled_url = click.style(requests.utils.requote_uri(url), bold=True)
        click.echo(
            f"Opening the login page in your browser. If this doesn't work, please visit the following URL:\n"
            f"{styled_url}\n"
        )

    auth_token = flow.login(options, org)
    options.set_access_token(auth_token.get("access_token"))
    fail_msg = "Sym could not verify this login. Please try again, or visit https://docs.symops.com/docs/login-sym-flow for more details."

    if not options.sym_api.verify_login(email):
        click.echo(fail_msg)
        return

    options.dprint(auth_token=auth_token)
    click.echo("Login succeeded")

    store_login_config(email, org, auth_token)


@click.command(short_help="Log out of your Sym account")
@click.make_pass_decorator(GlobalOptions, ensure=True)
def logout(options: GlobalOptions) -> None:
    if not Config.is_logged_in() and not options.access_token:
        click.secho("✖ You are already logged out!", fg="red")
        sys.exit(1)

    if options.access_token:
        click.secho(
            "✖ You are logged in via SYM_JWT, you must unset SYM_JWT manually", fg="red"
        )
        sys.exit(1)

    if Config.is_logged_in():
        Config.logout()
        click.secho("✔️  You successfully logged out!", fg="green")
