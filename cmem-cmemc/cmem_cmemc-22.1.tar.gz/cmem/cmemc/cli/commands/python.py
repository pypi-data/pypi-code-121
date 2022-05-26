"""DataIntegration python management commands."""
import sys
from re import match

import click

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.context import ApplicationContext
from cmem.cmempy.workspace.python import (
    install_package_by_file, install_package_by_name,
    list_packages, list_plugins,
    uninstall_package, update_plugins
)


def _looks_like_a_package(package: str) -> bool:
    """Check if a string looks like a package requirement string."""
    if match(r"^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*((==|<=|>=|>|<).*)?$", package):
        return True
    return False


@click.command(cls=CmemcCommand, name="install")
@click.argument(
    "PACKAGE",
    autocompletion=completion.python_package_files,
    type=click.Path(
        readable=True,
        allow_dash=False,
        dir_okay=False
    )
)
@click.pass_obj
def install_command(app: ApplicationContext, package):
    """Install a python package to the workspace.

    This command is basically a 'pip install' in the remote python
    environment.

    You can install a package by uploading a source distribution
    .tar.gz file, or by uploading a build distribution .whl file, or by
    specifying a package name, more precisely, a pip requirement
    specifier with a package name available on pypi.org
    (e.g. 'requests==2.27.1').
    """
    app.echo_info(
        f"Install package {package} ... ",
        nl=False
    )
    try:
        response = install_package_by_file(package_file=package)
    except FileNotFoundError as error:
        if not _looks_like_a_package(package):
            raise ValueError(
                f"{package} does not look like a package name or requirement "
                "string, and a file with this name also does not exists."
            ) from error
        response = install_package_by_name(package_name=package)
    for output_line in response["standardOutput"].splitlines():
        app.echo_debug(output_line)

    if response["success"]:
        app.echo_success("done")
        if len(response["errorOutput"].strip()) > 0:
            app.echo_warning(response["errorOutput"])
    else:
        app.echo_error("error")
        app.echo_debug(response["standardOutput"])
        if len(response["errorOutput"].strip()) > 0:
            app.echo_error(response["errorOutput"])
    app.echo_debug("Updated Plugins: " + str(update_plugins()))


@click.command(cls=CmemcCommand, name="uninstall")
@click.argument(
    "PACKAGE_NAME",
    autocompletion=completion.installed_package_names
)
@click.pass_obj
def uninstall_command(app: ApplicationContext, package_name):
    """Uninstall a python package from the workspace.

    This command is basically a 'pip uninstall' in the remote
    python environment.
    """
    app.echo_info(
        f"Uninstall package {package_name} ... ",
        nl=False
    )
    packages = list_packages()
    app.echo_debug(packages)
    if package_name not in [package["name"] for package in packages]:
        app.echo_error("not installed")
        sys.exit(1)
    response = uninstall_package(package_name=package_name)
    for output_line in response["standardOutput"].splitlines():
        app.echo_debug(output_line)
    if response["success"]:
        app.echo_success("done")
        if len(response["errorOutput"].strip()) > 0:
            app.echo_warning(response["errorOutput"])
    else:
        app.echo_error("error")
        app.echo_debug(response.content.decode())
    app.echo_debug("Updated Plugins: " + str(update_plugins()))


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only package identifier. "
         "This is useful for piping the IDs into other commands."
)
@click.pass_obj
def list_command(app: ApplicationContext, raw, id_only):
    """List installed python packages.

    This command is basically a 'pip list' in the remote python environment.

    It outputs a table of python package identifiers with version information.
    """
    packages = list_packages()
    if raw:
        app.echo_info_json(packages)
        return
    if id_only:
        for package in packages:
            app.echo_info(package["name"])
        return
    table = []
    for package in packages:
        table.append((
            package["name"],
            package["version"]
        ))
    app.echo_info_table(
        table,
        headers=["Name", "Version"],
        sort_column=0
    )


@click.command(cls=CmemcCommand, name="list-plugins")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only plugin identifier."
)
@click.pass_obj
def list_plugins_command(app: ApplicationContext, raw, id_only):
    """List installed workspace plugins.

    This commands lists all discovered plugins.
    Note that the plugin discovery is limited to specific packages.
    """
    plugins = list_plugins()
    if raw:
        app.echo_info_json(plugins)
        return
    if id_only:
        for plugin in sorted(plugins, key=lambda k: k["id"].lower()):
            app.echo_info(plugin["id"])
        return
    table = []
    for plugin in sorted(plugins, key=lambda k: k["id"].lower()):
        table.append((
            plugin["id"],
            plugin["pluginType"],
            plugin["label"],
        ))
    app.echo_info_table(
        table,
        headers=["ID", "Type", "Label"],
        sort_column=0
    )


@click.group(cls=CmemcGroup)
def python():
    """List, install, or uninstall python packages.

    Python packages are used to extend the DataIntegration workspace
    with python plugins. To get a list of installed packages, execute the
    list command.

    Warning: Installing packages from unknown sources is not recommended.
    Plugins are not verified for malicious code.
    """


python.add_command(install_command)
python.add_command(uninstall_command)
python.add_command(list_command)
python.add_command(list_plugins_command)
