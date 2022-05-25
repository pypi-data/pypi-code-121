import os
import sys
from typing import List

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# this line should be on the top to run it on a local environment as 'python vessl/cli/_main.py'
sys.path.append(project_root)

import click
import sentry_sdk
from click.decorators import pass_context
from sentry_sdk.integrations.logging import ignore_logger

import vessl
from vessl._version import __VERSION__
from vessl.cli._base import VesslGroup
from vessl.cli._util import prompt_choices
from vessl.cli.dataset import cli as dataset_cli
from vessl.cli.experiment import cli as experiment_cli
from vessl.cli.experiment import create as experiment_create
from vessl.cli.experiment import logs as experiment_logs
from vessl.cli.kernel_cluster import cli as kernel_cluster_cli
from vessl.cli.kernel_image import cli as kernel_image_cli
from vessl.cli.kernel_resource_spec import cli as kernel_resource_spec_cli
from vessl.cli.model import model_cli, model_repository_cli
from vessl.cli.organization import cli as organization_cli
from vessl.cli.project import cli as project_cli
from vessl.cli.ssh_key import cli as ssh_key_cli
from vessl.cli.sweep import cli as sweep_cli
from vessl.cli.volume import cli as volume_cli
from vessl.cli.workspace import cli as workspace_cli
from vessl.util.config import DEFAULT_CONFIG_PATH, VesslConfigLoader
from vessl.util.constant import API_HOST, EXPERIMENT_WORKING_DIR
from vessl.util.exception import (
    InvalidOrganizationError,
    InvalidProjectError,
    InvalidTokenError,
    VesslApiException,
)

# Configure Sentry in production
if API_HOST == "https://api.vessl.ai":
    sentry_sdk.init(
        os.environ.get(
            "SENTRY_DSN",
            "https://e46fcd750b3a443fbd5b9dbc970e4ecf@o386227.ingest.sentry.io/5911639",
        ),
        traces_sample_rate=1.0,
        ignore_errors=[VesslApiException],
    )
    sentry_sdk.set_tag("cli_version", __VERSION__)
    ignore_logger("vessl.util.logger")


def prompt_organizations() -> str:
    organizations = vessl.list_organizations()
    organization_count = len(organizations)

    new_organization_string = "Create new organization..."
    choices = [(x.name, i) for i, x in enumerate(organizations)] + [
        (new_organization_string, organization_count)
    ]
    choice = prompt_choices("Default organization", choices)

    if choice == organization_count:
        organization_name = click.prompt("Organization name", type=click.STRING)
        vessl.create_organization(organization_name)
    else:
        organization_name = organizations[choice].name

    return organization_name


@click.command(cls=VesslGroup)
@click.version_option()
@pass_context
def cli(ctx: click.Context):
    vessl.EXEC_MODE = "CLI"
    ctx.ensure_object(dict)


@cli.group(cls=VesslGroup, invoke_without_command=True)
@click.pass_context
@click.option("-t", "--access-token", type=click.STRING)
@click.option("-o", "--organization", type=click.STRING)
@click.option("-p", "--project", type=click.STRING)
@click.option("-f", "--credentials-file", type=click.STRING)
@click.option("--renew-token", is_flag=True)
def configure(
    ctx,
    access_token: str,
    organization: str,
    project: str,
    credentials_file: str,
    renew_token: bool,
):
    if ctx.invoked_subcommand:
        return

    try:
        vessl.configure_access_token(
            access_token=access_token,
            credentials_file=credentials_file,
            force_update=renew_token,
        )
    except InvalidTokenError:
        vessl.configure_access_token(force_update=True)

    try:
        vessl.configure_organization(
            organization_name=organization, credentials_file=credentials_file
        )
    except InvalidOrganizationError:
        organization_name = prompt_organizations()
        vessl.configure_organization(organization_name)

    try:
        vessl.configure_project(project_name=project, credentials_file=credentials_file)
    except InvalidProjectError:
        projects = vessl.list_projects()
        if len(projects) == 0:
            return

        project_name = prompt_choices("Default project", [x.name for x in projects])
        vessl.configure_project(project_name)

    print(f"Welcome, {vessl.vessl_api.user.display_name}!")


@configure.vessl_command()
@click.argument("organization", type=click.STRING, required=False)
def organization(organization: str):
    if organization is None:
        organization = prompt_organizations()
    vessl.configure_organization(organization)
    print(f"Saved to {DEFAULT_CONFIG_PATH}.")


@configure.vessl_command()
@click.argument("project", type=click.STRING, required=False)
def project(project: str):
    vessl.vessl_api.set_organization()

    if project is None:
        projects = vessl.list_projects()
        if len(projects) == 0:
            return

        project = prompt_choices("Default project", [x.name for x in projects])
    vessl.configure_project(project)
    print(f"Saved to {DEFAULT_CONFIG_PATH}.")


@configure.command()
def list():
    config = VesslConfigLoader()

    username = ""
    email = ""
    organization = config.default_organization or ""
    project = config.default_project or ""

    if config.access_token:
        vessl.vessl_api.api_client.set_default_header(
            "Authorization", f"Token {config.access_token}"
        )

        try:
            user = vessl.vessl_api.get_my_user_info_api()
            username = user.username
            email = user.email
        except VesslApiException as e:
            pass

    print(
        f"Username: {username}\n"
        f"Email: {email}\n"
        f"Organization: {organization}\n"
        f"Project: {project}"
    )


@cli.vessl_command()
@click.pass_context
@click.argument("command", nargs=-1, required=True)
def run(ctx, command: List[str]):
    args = []
    args.extend(["--command", " ".join(command)])
    args.extend(["--working-dir", f"{EXPERIMENT_WORKING_DIR}local/"])
    args.extend(["--upload-local-file", f".:{EXPERIMENT_WORKING_DIR}local/"])

    ctx.params = {}
    ctx.args = experiment_create.parse_args(ctx, args)
    ctx.forward(experiment_create)

    experiment_number = ctx.obj.get("experiment_number")
    ctx.params = {}
    ctx.args = experiment_logs.parse_args(ctx, [str(experiment_number), "--follow"])
    ctx.forward(experiment_logs)


cli.add_command(dataset_cli)
cli.add_command(experiment_cli)
cli.add_command(kernel_cluster_cli)
cli.add_command(kernel_image_cli)
cli.add_command(kernel_resource_spec_cli)
cli.add_command(model_cli)
cli.add_command(model_repository_cli)
cli.add_command(organization_cli)
cli.add_command(project_cli)
cli.add_command(ssh_key_cli)
cli.add_command(sweep_cli)
cli.add_command(volume_cli)
cli.add_command(workspace_cli)


if __name__ == "__main__":
    cli()
