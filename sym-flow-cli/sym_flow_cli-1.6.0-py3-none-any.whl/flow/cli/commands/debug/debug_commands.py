import click
from sym.shared.cli.helpers.sym_group import SymGroup

from sym.flow.cli.helpers.global_options import GlobalOptions

from .upload_directory import upload_directory
from .upload_file import upload_file
from .upload_terraform_output import upload_terraform_output


@click.group(
    cls=SymGroup,
    short_help="Utility commands for debugging a Sym Runtime",
    hidden=True,
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def debug(options: GlobalOptions) -> None:
    """Sym Flow CLI commands for debugging.

    For more details, see https://docs.symops.com/docs/support
    """


debug.add_command(upload_terraform_output)
debug.add_command(upload_file)
debug.add_command(upload_directory)
