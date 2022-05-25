import asyncio

import click

from jetpack import cron
from jetpack.cmd import _util
from jetpack.cmd._params import ENTRYPOINT_PARAMS
from jetpack.config import _symbols
from jetpack.config._symbols import Symbol
from jetpack.core._jetpack_function import JetpackFunction


@click.group(name="cron", help="Cronjob specific commands")
def cron_group() -> None:
    pass


@click.command(help="List existing cronjobs")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
def ls(entrypoint: str) -> None:
    _util.load_user_entrypoint(entrypoint)
    cronjobs = cron.get_jobs()
    if not cronjobs:
        click.echo("No cronjobs found")
        return
    click.echo(f"Found {len(cronjobs)} cronjobs:")
    for cronjob in cronjobs:
        click.echo("---")
        click.echo(cron.pretty_print(cronjob))


@click.command(help="Executes specified cronjob")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
@click.argument("symbol-name")
def exec(entrypoint: str, symbol_name: str) -> None:
    _util.load_user_entrypoint(entrypoint)
    func = _symbols.get_symbol_table().get_registered_symbols()[Symbol(symbol_name)]
    _, err = asyncio.run(JetpackFunction(func).exec(post_result=False))
    if err:
        raise err


cron_group.add_command(ls)
cron_group.add_command(exec)
