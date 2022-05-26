import click
from sym.shared.cli.helpers.sym_group import SymGroup

from sym.flow.cli.commands.bots.create import bots_create
from sym.flow.cli.commands.bots.delete import bots_delete
from sym.flow.cli.commands.bots.delete_identity import delete_bot_identity
from sym.flow.cli.commands.bots.list import bots_list
from sym.flow.cli.commands.bots.update_identity import update_bot_identity
from sym.flow.cli.helpers.global_options import GlobalOptions


@click.group(name="bots", cls=SymGroup, short_help="Perform operations on Sym Bot Users")
@click.make_pass_decorator(GlobalOptions, ensure=True)
def bots(options: GlobalOptions) -> None:
    """Operations on Sym Bot Users"""


bots.add_command(bots_create)
bots.add_command(bots_list)
bots.add_command(bots_delete)
bots.add_command(update_bot_identity)
bots.add_command(delete_bot_identity)
