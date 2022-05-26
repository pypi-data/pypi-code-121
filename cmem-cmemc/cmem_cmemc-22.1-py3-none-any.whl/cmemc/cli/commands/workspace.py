"""workspace commands for cmem command line interface."""
import os
from pathlib import Path

import click

from jinja2 import Template

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.commands.python import python
from cmem.cmempy.workspace import reload_workspace
from cmem.cmempy.workspace.export_ import export
from cmem.cmempy.workspace.import_ import import_workspace


@click.command(cls=CmemcCommand, name="export")
@click.option(
    "-o", "--overwrite",
    is_flag=True,
    help="Overwrite existing files. "
         "This is a dangerous option, so use it with care.",
)
@click.option(
    "--type", "marshalling_plugin",
    default="xmlZip",
    show_default=True,
    type=click.STRING,
    autocompletion=completion.marshalling_plugins,
    help="Type of the exported workspace file."
)
@click.option(
    "--filename-template", "-t", "template",
    default="{{date}}-{{connection}}.workspace",
    show_default=True,
    type=click.STRING,
    autocompletion=completion.workspace_export_templates,
    help="Template for the export file name. "
         "Possible placeholders are (Jinja2): "
         "{{connection}} (from the --connection option) and "
         "{{date}} (the current date as YYYY-MM-DD). "
         "The file suffix will be appended. "
         "Needed directories will be created."
)
@click.argument(
    "file",
    autocompletion=completion.workspace_files,
    required=False,
    type=click.Path(
        writable=True,
        allow_dash=False,
        dir_okay=False
    )
)
@click.pass_obj
def export_command(app, overwrite, marshalling_plugin, template, file):
    """Export the complete workspace (all projects) to a ZIP file.

    Depending on the requested type, this ZIP contains either a turtle file
    for each project (type rdfTurtle) or a substructure of resource files and
    XML descriptions (type xmlZip).

    The file name is optional and will be generated with by
    the template if absent.
    """
    ctx = click.get_current_context()
    if ctx.auto_envvar_prefix == "CMEMC_WORKSPACE_EXPORT":
        app.echo_warning(
            "The command workspace export is deprecated. "
            "Please use 'cmemc admin workspace export' instead."
        )
    if file is None:
        # prepare the template data and create the actual file incl. suffix
        template_data = app.get_template_data()
        file = Template(template).render(template_data) + ".zip"
    file = os.path.normpath(file)
    app.echo_info(f"Export workspace to {file} ... ", nl=False)
    if os.path.exists(file) and overwrite is not True:
        app.echo_error("file exists")
    else:
        # output directory is created lazy
        Path(
            os.path.dirname(file)
        ).mkdir(parents=True, exist_ok=True)
        # do the export
        export_data = export(marshalling_plugin)
        with open(file, "wb") as export_file:
            export_file.write(export_data)
        app.echo_success("done")


@click.command(cls=CmemcCommand, name="import")
@click.option(
    "--type", "marshalling_plugin",
    default="xmlZip",
    show_default=True,
    type=click.STRING,
    autocompletion=completion.marshalling_plugins,
    help="Type of the exported workspace file."
)
@click.argument(
    "file",
    autocompletion=completion.workspace_files,
    type=click.Path(
        readable=True,
        allow_dash=False,
        dir_okay=False
    )
)
@click.pass_obj
def import_command(app, file, marshalling_plugin):
    """Import the workspace from a file."""
    ctx = click.get_current_context()
    if ctx.auto_envvar_prefix == "CMEMC_WORKSPACE_IMPORT":
        app.echo_warning(
            "The command workspace import is deprecated. "
            "Please use 'cmemc admin workspace import' instead."
        )
    app.echo_info(f"Import workspace from {file} ... ", nl=False)
    import_workspace(file, marshalling_plugin)
    app.echo_success("done")


@click.command(cls=CmemcCommand, name="reload")
@click.pass_obj
def reload_command(app):
    """Reload the workspace from the backend."""
    ctx = click.get_current_context()
    if ctx.auto_envvar_prefix == "CMEMC_WORKSPACE_RELOAD":
        app.echo_warning(
            "The command workspace reload is deprecated. "
            "Please use 'cmemc admin workspace reload' instead."
        )
    app.echo_info("Reload workspace  ... ", nl=False)
    reload_workspace()
    app.echo_success("done")


@click.group(cls=CmemcGroup, )
def workspace():
    """Import, export and reload the project workspace."""


workspace.add_command(export_command)
workspace.add_command(import_command)
workspace.add_command(reload_command)
workspace.add_command(python)
