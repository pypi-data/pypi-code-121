import click
from sym.shared.cli.helpers.sym_group import SymGroup

from sym.flow.cli.commands.policies.generate import policies_generate
from sym.flow.cli.commands.policies.wizard import policies_wizard


@click.group(cls=SymGroup, short_help="Manipulate IAM Strategies")
def policies() -> None:
    pass


policies.add_command(policies_wizard)
policies.add_command(policies_generate)
