from typing import Optional

import click

from mlfoundry.login import login as login_


@click.command(short_help="Store API key in the local file system")
@click.option(
    "--tracking_uri",
    type=str,
    default=None,
    help="Tracking server host",
)
@click.option(
    "--relogin",
    is_flag=True,
    show_default=True,
    default=False,
    help="Overwrite existing API key for the given `tracking_uri`",
)
def login(tracking_uri: Optional[str], relogin: bool):
    login_(tracking_uri=tracking_uri, relogin=relogin)
