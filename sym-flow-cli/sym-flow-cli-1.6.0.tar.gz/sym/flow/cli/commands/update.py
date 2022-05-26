import click
from sym.shared.cli.helpers.updater import SymUpdater

from sym.flow.cli.helpers.global_options import GlobalOptions


@click.command(short_help="Update the Sym Flow CLI")
@click.make_pass_decorator(GlobalOptions)
def update(options: GlobalOptions) -> None:
    SymUpdater(debug=options.debug).manual_update()
