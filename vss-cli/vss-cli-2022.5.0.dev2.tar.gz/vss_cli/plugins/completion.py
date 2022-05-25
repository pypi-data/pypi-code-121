"""Auto-completion for VSS CLI (vss-cli)."""
import click
from click.shell_completion import get_completion_class

from vss_cli.cli import pass_context


@click.group(
    'completion',
    short_help='Output shell completion code for '
    'the specified shell (bash or zsh or fish).',
)
@pass_context
def cli(ctx):
    """Output shell completion code for the specified shell.

    Supported shells: bash, zsh and fish.
    """


def dump_script(shell: str) -> None:
    """Dump the script content."""
    prog_name = "vss-cli"
    complete_var = '_%s_COMPLETE' % (prog_name.replace('-', '_')).upper()
    comp_cls = get_completion_class(shell)
    comp = comp_cls(cli, dict(), prog_name, complete_var)
    click.echo(comp.source())


@cli.command()
@pass_context
def bash(ctx):
    """Output shell completion code for bash."""
    dump_script("bash")


@cli.command()
@pass_context
def zsh(ctx):
    """Output shell completion code for zsh."""
    dump_script("zsh")


@cli.command()
@pass_context
def fish(ctx):
    """Output shell completion code for fish."""
    dump_script("fish")
