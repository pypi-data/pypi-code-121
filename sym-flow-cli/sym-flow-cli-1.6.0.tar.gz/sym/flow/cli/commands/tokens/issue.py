import re
from datetime import timedelta
from typing import Optional

import click

from sym.flow.cli.errors import InvalidExpiryError
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions


def to_timedelta(ctx: click.Context, param, value) -> timedelta:
    """Parses the shorthand expiry and returns a timedelta if it is in an accepted format"""

    # Accepted expiries are an integer (non-zero, non-zero-leading) followed by [s, m, d, or mo]
    expiry_pattern = re.compile(r"^([1-9][0-9]*)(\w{1,2})$")
    if expiry_value := expiry_pattern.match(value):
        duration_value = int(expiry_value.group(1))
        duration_unit = expiry_value.group(2)
        if duration_unit == "s":
            return timedelta(seconds=duration_value)
        elif duration_unit == "m":
            return timedelta(minutes=duration_value)
        elif duration_unit == "d":
            return timedelta(days=duration_value)
        elif duration_unit == "mo":
            return timedelta(days=30 * duration_value)

    raise InvalidExpiryError(value)


@click.command(name="issue", short_help="Issue a new Sym Token")
@click.make_pass_decorator(GlobalOptions, ensure=True)
@click.option(
    "-u",
    "--username",
    help="The name of the bot-user to issue the token for",
    prompt=True,
    required=True,
)
@click.option(
    "-e",
    "--expiry",
    help="The TTL for the token in shorthand",
    prompt=True,
    required=True,
    callback=to_timedelta,
)
@click.option(
    "-l",
    "--label",
    help="An optional label for the token",
    required=False,
)
def tokens_issue(
    options: GlobalOptions, username: str, expiry: timedelta, label: Optional[str]
) -> None:
    """
    Issues a new token for the bot-user identified by the given username.
    The expiry is a time duration in shorthand, e.g. `30d`

    \b
    Accepted durations are:
        - `s` = seconds
        - `m` = minutes
        - `d` = days
        - `mo` = months (30 days)
    """
    access_token = options.sym_api.create_token(username.strip(), expiry, label)
    click.secho(
        f"{access_token}",
        fg="green",
    )
