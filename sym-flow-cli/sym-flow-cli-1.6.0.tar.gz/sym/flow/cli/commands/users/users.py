import click
from sym.shared.cli.helpers.sym_group import SymGroup

from sym.flow.cli.commands.users.create import users_create
from sym.flow.cli.commands.users.delete import users_delete
from sym.flow.cli.commands.users.delete_identity import delete_user_identity
from sym.flow.cli.commands.users.list import users_list
from sym.flow.cli.commands.users.update import users_update
from sym.flow.cli.commands.users.update_identity import update_user_identity
from sym.flow.cli.helpers.global_options import GlobalOptions


@click.group(name="users", cls=SymGroup, short_help="Perform operations on Sym Users")
@click.make_pass_decorator(GlobalOptions, ensure=True)
def users(options: GlobalOptions) -> None:
    """Operations on Users"""


users.add_command(users_create)
users.add_command(users_list)
users.add_command(users_update)
users.add_command(users_delete)
users.add_command(update_user_identity)
users.add_command(delete_user_identity)
