"""The main command line interface."""

import os
from subprocess import CalledProcessError  # nosec
import sys
import traceback

import click

import requests.exceptions

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import (
    admin,
    config,
    dataset,
    graph,
    project,
    query,
    vocabulary,
    workflow
)
from cmem.cmemc.cli.context import CONTEXT
from cmem.cmemc.cli.exceptions import (
    InvalidConfiguration
)
from cmem.cmemc.cli.utils import (
    extract_error_message,
    get_version,
    is_completing,
    print_manual,
    print_manual_graph
)
from cmem.cmemc.cli.commands import CmemcGroup

cmemc_version = get_version()

version = sys.version_info
PYTHON_VERSION = f"{version.major}.{version.minor}.{version.micro}"
PYTHON_EXPECTED = "3.9"
PYTHON_GOT = f"{version.major}.{version.minor}"
if PYTHON_EXPECTED != PYTHON_GOT:
    # test for environment which indicates that we are in completion mode
    if not is_completing():
        CONTEXT.echo_warning(
            "Warning: You are running cmemc under a non-tested python "
            f"environment (expected {PYTHON_EXPECTED}, got {PYTHON_GOT})"
        )

# set the user-agent environment for the http request headers
os.environ["CMEM_USER_AGENT"] = f"cmemc/{cmemc_version} " \
                                f"(Python {PYTHON_VERSION})"

# https://github.com/pallets/click/blob/master/examples/complex/complex/cli.py
CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='CMEMC',
    help_option_names=['-h', '--help']
)


@click.group(cls=CmemcGroup, context_settings=CONTEXT_SETTINGS)
@click.option(
    '-c', '--connection',
    type=click.STRING,
    autocompletion=completion.connections,
    help='Use a specific connection from the config file.'
)
@click.option(
    '--config-file',
    autocompletion=completion.ini_files,
    type=click.Path(
        readable=True,
        allow_dash=False,
        dir_okay=False
    ),
    default=CONTEXT.config_file_default,
    show_default=True,
    help='Use this config file instead of the default one.'
)
@click.option(
    '-q', '--quiet',
    is_flag=True,
    help='Suppress any non-error info messages.'
)
@click.option(
    '-d', '--debug',
    is_flag=True,
    help='Output debug messages and stack traces after errors.'
)
@click.version_option(
    version=cmemc_version,
    message="%(prog)s, version %(version)s, "
            f"running under python {PYTHON_VERSION}"
)
@click.pass_context
def cli(ctx, debug, quiet, config_file, connection):  # noqa: D403
    """eccenca Corporate Memory Control (cmemc).

    cmemc is the eccenca Corporate Memory Command Line Interface (CLI).

    Available commands are grouped by affecting resource type (such as graph,
    project and query).
    Each command and group has a separate --help screen for detailed
    documentation.
    In order to see possible commands in a group, simply
    execute the group command without further parameter (e.g. cmemc project).

    If your terminal supports colors, these coloring rules are applied:
    Groups are colored in white; Commands which change data are colored in
    red; all other commands as well as options are colored in green.

    Please also have a look at the cmemc online documentation:

                        https://eccenca.com/go/cmemc

    cmemc is © 2022 eccenca GmbH, licensed under the Apache License 2.0.
    """
    ctx.obj = CONTEXT
    # hidden feature: 'CMEMC_MANUAL=true cmemc -q config list' will output
    #     the whole markdown manual
    if os.getenv("CMEMC_MANUAL"):
        print_manual(ctx)
        ctx.exit()
    # hidden feature: 'CMEMC_MANUAL_GRAPH=true cmemc -q config list' will
    # output the documentation graph
    if os.getenv("CMEMC_MANUAL_GRAPH"):
        print_manual_graph(ctx)
        ctx.exit()
    ctx.obj.set_quiet(quiet)
    ctx.obj.set_debug(debug)
    ctx.obj.set_config_file(config_file)
    try:
        ctx.obj.set_connection(connection)
    except InvalidConfiguration as error:
        # if config is broken still allow for "config edit"
        # means: do not forward this exception if "config edit"
        if " ".join(sys.argv).find("config edit") == -1:
            raise error


cli.add_command(admin.admin)
cli.add_command(config.config)
cli.add_command(dataset.dataset)
cli.add_command(graph.graph)
cli.add_command(project.project)
cli.add_command(query.query)
cli.add_command(vocabulary.vocabulary)
cli.add_command(workflow.workflow)


def main():
    """Start the command line interface."""
    try:
        cli()  # pylint: disable=no-value-for-parameter
    except (
            CalledProcessError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            ValueError,
            IOError,
            NotImplementedError,
            KeyError
    ) as error:
        if is_completing():
            # if currently autocompleting -> silently die with exit 1
            sys.exit(1)
        CONTEXT.check_versions()
        CONTEXT.echo_debug(traceback.format_exc())
        CONTEXT.echo_error(extract_error_message(error))
        sys.exit(1)
