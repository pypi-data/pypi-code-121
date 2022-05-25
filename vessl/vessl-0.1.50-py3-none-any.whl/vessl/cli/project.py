import sys

import click

import vessl
from vessl.cli._base import VesslGroup, vessl_argument
from vessl.cli._util import (
    Endpoint,
    format_url,
    generic_prompter,
    print_data,
    print_table,
    prompt_choices,
)
from vessl.cli.organization import organization_name_option
from vessl.project import create_project, list_projects, read_project
from vessl.util.exception import InvalidProjectError


def project_name_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> str:
    projects = list_projects()
    return prompt_choices("Project", [x.name for x in projects])


@click.command(name="project", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=project_name_prompter
)
@organization_name_option
def read(name: str):
    project = read_project(project_name=name)
    print_data(
        {
            "ID": project.id,
            "Name": project.name,
            "Experiments": project.experiment_summary.total,
        }
    )


@cli.vessl_command()
@organization_name_option
def list():
    projects = list_projects()
    print_table(
        projects,
        ["ID", "Name", "Experiments"],
        lambda x: [x.id, x.name, x.experiment_summary.total],
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=generic_prompter("Project name")
)
@click.option("-m", "--description", type=click.STRING)
@organization_name_option
def create(name: str, description: str):
    project = create_project(
        project_name=name,
        description=description,
    )
    print(
        f"Created '{project.name}'.\n"
        f"For more info: {format_url(Endpoint.project.format(project.organization.name, project.name))}"
    )


### Deprecate for now
# @cli.vessl_command()
# @vessl_argument(
#     "name", type=click.STRING, required=True, prompter=version_control_project_name_prompter,
# )
# @organization_name_option
# def clone(name: str):
#     clone_project(project_name=name)


def project_name_callback(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
):
    if vessl.vessl_api.organization is None:
        vessl.vessl_api.set_organization()

    try:
        project_name = vessl.vessl_api.set_project(value)
        print(f"Project: {project_name}")
    except InvalidProjectError:
        print("Invalid project. Please choose a project using `vessl configure`.")
        sys.exit(1)


# Ensure this is called before other options with `is_eager=True` for
# other callbacks that need organization to be preconfigured.
project_name_option = click.option(
    "--project",
    "project_name",
    type=click.STRING,
    hidden=True,
    is_eager=True,
    expose_value=False,
    callback=project_name_callback,
    help="Override default project.",
)
