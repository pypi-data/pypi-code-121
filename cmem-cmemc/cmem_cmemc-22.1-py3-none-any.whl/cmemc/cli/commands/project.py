"""DataIntegration project commands for the cmem command line interface."""
import os
from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile

import click

from jinja2 import Template

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmempy.config import get_di_api_endpoint
from cmem.cmempy.plugins.marshalling import (
    get_extension_by_plugin,
    get_marshalling_plugins
)
from cmem.cmempy.workspace.projects.export_ import export_project
from cmem.cmempy.workspace.projects.import_ import (
    import_from_upload_start,
    import_from_upload_status,
    upload_project
)
from cmem.cmempy.workspace.projects.project import (
    delete_project,
    get_failed_tasks_report,
    get_projects,
    make_new_project,
)


def _show_type_list(app):
    """Output the list of project export types.

    Internally this is named marshalling plugin.

    Args:
        app (ApplicationContext): the click cli app context.
    """
    types = get_marshalling_plugins()
    table = []
    for _ in types:
        id_ = _["id"]
        label = _["label"]
        description = _["description"].partition("\n")[0]
        row = [
            id_,
            f"{label}: {description}",
        ]
        table.append(row)
    app.echo_info_table(
        table,
        headers=["Export Type", "Description"],
        sort_column=1
    )


@click.command(cls=CmemcCommand, name="open")
@click.argument(
    "project_ids",
    nargs=-1,
    required=True,
    type=click.STRING,
    autocompletion=completion.project_ids
)
@click.pass_obj
def open_command(app, project_ids):
    """Open projects in the browser.

    With this command, you can open a project in the workspace in
    your browser to change them.

    The command accepts multiple projects IDs which results in
    opening multiple browser tabs.
    """
    projects = get_projects()
    for _ in project_ids:
        if _ not in (p["name"] for p in projects):
            raise ValueError(f"Project '{_}' not found.")
        open_project_uri = f"{get_di_api_endpoint()}/workbench/projects/{_}"
        app.echo_debug(f"Open {_}: {open_project_uri}")
        click.launch(open_project_uri)


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only project identifier and no labels or other "
         "meta data. This is useful for piping the IDs into other commands."
)
@click.pass_obj
def list_command(app, raw, id_only):
    """List available projects.

    Outputs a list of project IDs which can be used as reference for
    the project create, delete, export and import commands.
    """
    projects = get_projects()
    if raw:
        app.echo_info_json(projects)
        return
    if id_only:
        for _ in sorted(projects, key=lambda k: k["name"].lower()):
            app.echo_result(_["name"])
        return
    # output a user table
    table = []
    for _ in projects:
        row = [
            _["name"],
            _["metaData"]["label"],
        ]
        table.append(row)
    app.echo_info_table(
        table,
        headers=["Project ID", "Label"],
        sort_column=1
    )


@click.command(cls=CmemcCommand, name="delete")
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Delete all projects. "
         "This is a dangerous option, so use it with care.",
)
@click.argument(
    "project_ids",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.project_ids
)
@click.pass_obj
def delete_command(app, all_, project_ids):
    """Delete project(s).

    This deletes existing data integration projects from Corporate Memory.
    Projects will be deleted without prompting!

    Example: cmemc project delete my_project

    Projects can be listed by using the 'cmemc project list' command.
    """
    all_projects = get_projects()
    if project_ids == () and not all_:
        raise ValueError("Either specify at least one project ID "
                         + "or use the --all option to delete all projects.")
    if all_:
        # in case --all is given, a list of project is fetched
        project_ids = (
            [currentProjects["name"] for currentProjects in all_projects]
        )
    # avoid double removal
    project_ids = list(set(project_ids))

    # test if projects exist
    for project_id in project_ids:
        if project_id not in ([_["name"] for _ in all_projects]):
            raise ValueError(f"Project {project_id} does not exist.")

    count = len(project_ids)
    current = 1
    for project_id in project_ids:
        app.echo_info(
            f"Delete project {current}/{count}: {project_id} ... ",
            nl=False
        )
        delete_project(project_id)
        app.echo_success("done")
        current = current + 1


@click.command(cls=CmemcCommand, name="create")
@click.argument(
    "project_ids",
    nargs=-1,
    required=True,
    type=click.STRING
)
@click.pass_obj
def create_command(app, project_ids):
    """Create empty new project(s).

    This creates one or more new projects.
    Existing projects will not be overwritten.

    Example: cmemc project create my_project

    Projects can be listed by using the 'cmemc project list' command.
    """
    # avoid double creation
    project_ids = list(set(project_ids))

    all_projects = get_projects()
    # test if projects exist
    for project_id in project_ids:
        if project_id in ([_["name"] for _ in all_projects]):
            raise ValueError(f"Project {project_id} already exist.")

    count = len(project_ids)
    current = 1
    for project_id in project_ids:
        app.echo_info(
            f"Create new project {current}/{count}: {project_id} ... ",
            nl=False
        )
        app.echo_debug(get_projects())
        make_new_project(project_id)
        app.echo_success("done")
        current = current + 1


# pylint: disable=too-many-arguments,too-many-locals
@click.command(cls=CmemcCommand, name="export")  # noqa: C901
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Export all projects.",
)
@click.option(
    "-o", "--overwrite",
    is_flag=True,
    help="Overwrite existing files. This is a dangerous option, "
         "so use it with care.",
)
@click.option(
    "--output-dir",
    default=".",
    show_default=True,
    type=click.Path(
        writable=True,
        file_okay=False
    ),
    # autocompletion=directories,
    help="The base directory, where the project files will be created. "
         "If this directory does not exist, it will be silently created."
)
@click.option(
    "--type", "marshalling_plugin",
    default="xmlZip",
    show_default=True,
    type=click.STRING,
    autocompletion=completion.marshalling_plugins,
    help="Type of the exported project file(s). Use the --help-types option "
         "or tab completion to see a list of possible types."
)
@click.option(
    "--filename-template", "-t", "template",
    default="{{date}}-{{connection}}-{{id}}.project",
    show_default=True,
    type=click.STRING,
    autocompletion=completion.project_export_templates,
    help="Template for the export file name(s). "
         "Possible placeholders are (Jinja2): "
         "{{id}} (the project ID), "
         "{{connection}} (from the --connection option) and "
         "{{date}} (the current date as YYYY-MM-DD). "
         "The file suffix will be appended. "
         "Needed directories will be created."
)
@click.option(
    "--extract",
    is_flag=True,
    help="Export projects to a directory structure instead of a ZIP archive. "
         "Note that the --filename-template "
         "option is ignored here. Instead, a sub-directory per exported "
         "project is created under the output directory. "
         "Also note that not all export types are extractable.",
)
@click.option(
    "--help-types",
    is_flag=True,
    help="Lists all possible export types."
)
@click.argument(
    "project_ids",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.project_ids
)
@click.pass_obj
def export_command(
        app, all_, project_ids, overwrite, marshalling_plugin,
        template, output_dir, extract, help_types):
    """Export project(s) to file(s).

    Projects can be exported with different export formats.
    The default type is a zip archive which includes meta data as well
    as dataset resources.
    If more than one project is exported, a file is created for each project.
    By default, these files are created in the current directory and with
    a descriptive name (see --template option default).

    Example: cmemc project export my_project

    Available projects can be listed by using the 'cmemc project list' command.

    You can use the template string to create subdirectories as well:
    cmemc config list | parallel -I% cmemc -c % project export --all
    -t "dump/{{connection}}/{{date}}-{{id}}.project"
    """
    if help_types:
        _show_type_list(app)
        return

    all_projects = get_projects()
    if project_ids == () and not all_:
        raise ValueError("Either specify at least one project ID "
                         + "or use the --all option to export all projects.")
    if all_:
        # in case --all is given, a list of project is fetched
        project_ids = ([_["name"] for _ in all_projects])
    # avoid double export
    project_ids = list(set(project_ids))

    # test if projects exist
    for project_id in project_ids:
        if project_id not in ([_["name"] for _ in all_projects]):
            raise ValueError(f"Project {project_id} does not exist.")

    extractable_types = ("xmlZip", "xmlZipWithoutResources")
    if extract and marshalling_plugin not in extractable_types:
        raise ValueError(
            f"The export type {marshalling_plugin} can not be extracted. "
            f"Use one of {extractable_types}."
        )

    template_data = app.get_template_data()

    count = len(project_ids)
    current = 1
    for project_id in project_ids:
        # prepare the template data and prepare target path name
        template_data.update(id=project_id)
        if extract:
            # this name is only used of display
            # the ZIP has first level directory
            local_name = project_id
        else:
            local_name = Template(template).render(template_data)\
                + "." + get_extension_by_plugin(marshalling_plugin)
        # join with given output directory and normalize full path
        export_path = os.path.normpath(os.path.join(output_dir, local_name))

        app.echo_info(
            f"Export project {current}/{count}: "
            f"{project_id} to {export_path} ... ",
            nl=False
        )
        if os.path.exists(export_path) and overwrite is not True:
            app.echo_error("target file or directory exists")
            continue

        os.makedirs(output_dir, exist_ok=True)

        if extract:
            export_data = export_project(project_id, marshalling_plugin)
            # do the export to a temp file and extract it afterwards
            with tempfile.NamedTemporaryFile() as tmp_file:
                app.echo_debug(f"Temporary file is {tmp_file.name}")
                tmp_file.write(export_data)
                shutil.rmtree(export_path, ignore_errors=True)
                with ZipFile(tmp_file, 'r') as _:
                    _.extractall(output_dir)
        else:
            export_data = export_project(project_id, marshalling_plugin)
            # create parent directory
            os.makedirs(Path(export_path).parent.absolute(), exist_ok=True)
            with open(export_path, "wb") as _:
                _.write(export_data)

        app.echo_success("done")
        current = current + 1


@click.command(cls=CmemcCommand, name="import")
@click.argument(
    "path",
    autocompletion=completion.project_files,
    type=click.Path(
        allow_dash=False,
        dir_okay=True,
        readable=True,
        exists=True
    )
)
@click.argument(
    "project_id",
    type=click.STRING,
    autocompletion=completion.project_ids
)
@click.option(
    "-o", "--overwrite",
    is_flag=True,
    help="Overwrite an existing project. This is a dangerous option, "
         "so use it with care.",
)
@click.pass_obj
def import_command(app, path, project_id, overwrite):
    """Import a project from a file or directory.

    Example: cmemc project import my_project.zip my_project
    """
    if not overwrite:
        if project_id in ([_["name"] for _ in get_projects()]):
            raise ValueError(f"Project {project_id} is already there.")
    if os.path.isdir(path):
        if not os.path.isfile(
            os.path.normpath(os.path.join(path, "config.xml"))
        ):
            # fail early if directory is not an export
            raise ValueError(
                f"Directory {path} seems not to be a export directory."
            )

        app.echo_info(
            f"Import directory {path} to project {project_id} ... ",
            nl=False
        )
        # in case of an directory, we zip it to a temp file
        app.echo_info("zipping ... ", nl=False)
        with tempfile.NamedTemporaryFile() as _:
            shutil.make_archive(
                _.name,
                'zip',
                base_dir=Path(path).name,
                root_dir=Path(path).parent.absolute()
            )
            # make_archive adds a .zip automatically ...
            uploaded_file = _.name + ".zip"
            app.echo_debug(f"Uploaded file is {uploaded_file}")
    else:
        app.echo_info(
            f"Import file {path} to project {project_id} ... ",
            nl=False
        )
        uploaded_file = path

    # upload file and get validation report
    validation_response = upload_project(uploaded_file)
    if "errorMessage" in validation_response.keys():
        raise ValueError(validation_response["errorMessage"])
    import_id = validation_response["projectImportId"]
    app.echo_debug(
        f"File {uploaded_file} uploaded: {validation_response}"
    )

    # start import of project from upload using import ID as a reference
    import_from_upload_start(
        import_id=import_id,
        project_id=project_id,
        overwrite_existing=overwrite
    )

    # loop until "success" boolean is in status response
    status = import_from_upload_status(import_id)
    while "success" not in status.keys():
        status = import_from_upload_status(import_id)
    if status["success"] is True:
        app.echo_success("done")
        # output warnings in case there are failed tasks errors
        for _ in get_failed_tasks_report(project_id):
            app.echo_warning(_["errorMessage"])
    else:
        app.echo_error(" error")
    app.echo_debug(f"last import status: {status}")


@click.group(cls=CmemcGroup)
def project():
    """List, import, export, create, delete or open projects.

    Projects are identified by an PROJECTID. The get a list of existing
    projects, execute the list command or use tab-completion.
    """


project.add_command(open_command)
project.add_command(list_command)
project.add_command(export_command)
project.add_command(import_command)
project.add_command(delete_command)
project.add_command(create_command)
