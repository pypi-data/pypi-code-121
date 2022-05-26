import click
from sym.shared.cli.helpers.sym_group import SymGroup

from sym.flow.cli.commands.tokens.issue import tokens_issue
from sym.flow.cli.commands.tokens.list import tokens_list
from sym.flow.cli.commands.tokens.revoke import tokens_revoke
from sym.flow.cli.helpers.global_options import GlobalOptions


@click.group(name="tokens", cls=SymGroup, short_help="Perform operations on Sym Tokens")
@click.make_pass_decorator(GlobalOptions, ensure=True)
def tokens(options: GlobalOptions) -> None:
    """Operations on Tokens"""


tokens.add_command(tokens_issue)
tokens.add_command(tokens_revoke)
tokens.add_command(tokens_list)
