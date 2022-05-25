"""Compute plugin for VSS CLI (vss-cli)."""
import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from vss_cli.cli import pass_context
from vss_cli.config import Configuration


@with_plugins(iter_entry_points('vss_cli.contrib.compute'))
@click.group('compute', short_help='Manage VMs, networks, folders, etc.')
@pass_context
def cli(ctx: Configuration):
    """Compute related resources.

    Such as virtual machines, networks supported operating systems,
    logical folders, OVA/OVF images, floppy images, ISO images and more.
    """
    with ctx.spinner(disable=ctx.debug) as spinner_cls:
        ctx.load_config(spinner_cls=spinner_cls)


from vss_cli.plugins.compute_plugins import (  # isort:skip
    domain,
    floppy,
    folder,
    image,
    inventory,
    iso,
    net,
    os as compute_os,
    template,
    vm,
)  # pylint: disable=unused-import
