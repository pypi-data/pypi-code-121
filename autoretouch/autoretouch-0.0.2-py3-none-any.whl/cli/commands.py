import contextlib
import json
import os
import click
import click_log
import logging

from typing import Optional
from uuid import UUID

from autoretouch.api_client.client import AutoRetouchAPIClient, USER_CONFIG, USER_CONFIG_PATH

logger = logging.getLogger("autoretouch-python-client")
logger.setLevel("INFO")
click_log.basic_config(logger)
click_log.ColorFormatter.colors["info"] = dict(fg="green")


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


CONTEXT_SETTINGS = dict(help_option_names=['--help', '-h'])


@click.group(context_settings=CONTEXT_SETTINGS)
def autoretouch_cli():
    pass


@click.command()
@click_log.simple_verbosity_option(logger)
def login():
    """
    authenticate with your autoretouch account

    create/fetch credentials from the environment variables
        - AUTORETOUCH_REFRESH_TOKEN
        or
        - AUTORETOUCH_CREDENTIALS_PATH (default = home/.config/autoretouch-credentials.json)
    or trigger Auth0 device flow if none of the above are set and store the obtained credentials
    in AUTORETOUCH_CREDENTIALS_PATH
    """
    AutoRetouchAPIClient().login()


@click.command()
@click_log.simple_verbosity_option(logger)
def logout():
    """
    revoke and remove stored refresh token from disk
    """
    AutoRetouchAPIClient().revoke_credentials().logout()


@click.group()
def config():
    """
    configure/show which organization and workflow are used by default
    """
    pass


@click.command(name="get")
@click_log.simple_verbosity_option(logger)
def config_get():
    """
    show the organization and workflow that are currently used by default
    """
    for key, value in USER_CONFIG.items():
        click.echo(key)
        for k, v in value.items():
            click.echo(f"\t{k}: {v}")


def autocomplete_user_organizations(ctx: click.core.Context, param: click.core.Argument, incomplete: str):
    with contextlib.redirect_stderr(open(os.devnull, 'w')), contextlib.redirect_stdout(open(os.devnull, 'w')):
        try:
            return [str(k.id) for k in AutoRetouchAPIClient().get_organizations() if k.name.startswith(incomplete)]
        except Exception as e:
            return []


def autocomplete_user_workflows(ctx: click.core.Context, param: click.core.Argument, incomplete: str):
    with contextlib.redirect_stderr(open(os.devnull, 'w')), contextlib.redirect_stdout(open(os.devnull, 'w')):
        try:
            return [str(k.id) for k in AutoRetouchAPIClient().get_workflows() if k.name.startswith(incomplete)]
        except Exception as e:
            return []


@click.command(name="set")
@click.option("--organization-id", "-o", default=None, shell_complete=autocomplete_user_organizations,
              help="the id of the organization that the autoretouch cli will use by default")
@click.option("--workflow-id", "-w", default=None, shell_complete=autocomplete_user_workflows,
              help="the id of the workflow that the autoretouch cli will use by default")
@click_log.simple_verbosity_option(logger)
def config_set(organization_id, workflow_id):
    """
    configure the organization and/or workflow that are used by default
    """
    client = AutoRetouchAPIClient()
    if organization_id is not None:
        org = client.get_organization(organization_id)
        new_org = {"organization": {"name": org.name, "id": org.id}}
    else:
        new_org = {"organization": USER_CONFIG["organization"]}
    if workflow_id is not None:
        wf = client.get_workflow(workflow_id)
        new_wf = {"workflow": {"name": wf.name, "id": wf.id}}
    else:
        new_wf = {"workflow": USER_CONFIG["workflow"]}
    new_config = {**new_org, **new_wf}
    with open(USER_CONFIG_PATH, "w") as f:
        f.write(json.dumps(new_config, cls=UUIDEncoder))


@click.command()
@click.option('--format', '-f', default="text", type=click.Choice(['text', 'json'], case_sensitive=False),
              help='the output format. Default=text')
@click_log.simple_verbosity_option(logger)
def organizations(format):
    """
    list all your organizations
    """
    orgs = AutoRetouchAPIClient().get_organizations()
    if format == 'text':
        for org in orgs:
            click.echo(f"{org.name}: {org.id}")
    if format == 'json':
        click.echo(json.dumps([o.to_dict() for o in orgs], indent=4, cls=UUIDEncoder))


@click.command()
@click.argument('organization_id', default=None, shell_complete=autocomplete_user_organizations,
                required=False)
@click.option('--format', '-f', default="text", type=click.Choice(['text', 'json'], case_sensitive=False),
              help='the output format. Default=text')
@click_log.simple_verbosity_option(logger)
def organization(organization_id, format):
    """
    show details of given organization

    ORGANIZATION_ID: id of the organization you want to get. If not provided, default to the organization set in your config
    """
    org = AutoRetouchAPIClient().get_organization(organization_id)
    if format == 'text':
        click.echo(f"{org.name}: {org.id}")
    if format == 'json':
        click.echo(json.dumps(org, indent=4))


@click.command()
@click.argument('images', type=click.File('rb'), nargs=-1)
@click_log.simple_verbosity_option(logger)
def upload(images):
    """
    upload an image/images to autoretouch
    IMAGES: path to the images to upload
    """
    client = AutoRetouchAPIClient()
    for file in images:
        click.echo(f"{file.name} is uploaded as {client.upload_image_from_stream(file)}")


@click.command("balance")
@click_log.simple_verbosity_option(logger)
def balance():
    """
    show your organization's credit balance

    default format: autoretouch credits - corresponds to € cents excl. VAT
    """
    click.echo(AutoRetouchAPIClient().get_balance())


@click.command()
@click.argument('input', type=click.Path(exists=True), required=True)
@click.argument('output', type=click.Path(exists=True), required=True)
@click.option('--workflow-id', '-w', required=False, shell_complete=autocomplete_user_workflows,
              help="id of the workflow to use for processing. Default to the workflow set in your config")
@click.option('--yes', '-y', required=False, is_flag=True,
              help="skip confirmation")
@click_log.simple_verbosity_option(logger)
def process(input: str, output: str, workflow_id: Optional[UUID], yes: bool = False):
    """
    process an image or a folder of images and wait for the result

    INPUT: path to an image or to a folder of images

    OUTPUT: destination folder for processed image(s)

    """
    client = AutoRetouchAPIClient()
    if os.path.isfile(input):
        client.process_image(input, output, workflow_id=workflow_id)
    else:
        images = client.find_images(input)
        if not yes:
            click.confirm(f"Are you sure you want to process {len(images)} images?", abort=True)
        logger.info(f"Uploading and processing {len(images)} images ...")
        client.process_folder(input, output, workflow_id=workflow_id)
    logger.info("Done.")


@click.command()
@click.option('--organization-id', "-o", default=None, shell_complete=autocomplete_user_organizations,
              help="id of the organization you want to get. "
                   "If not provided, default to the organization set in your config")
@click.option('--format', '-f', default="text", type=click.Choice(['text', 'json'], case_sensitive=False),
              help='the output format. Default=text')
@click_log.simple_verbosity_option(logger)
def workflows(organization_id, format):
    """
    list the workflows defined in an organization
    """
    client = AutoRetouchAPIClient()
    workflows = client.get_workflows(organization_id)
    if format == 'text':
        for workflow in workflows:
            click.echo(f"{workflow.name}: {workflow.id}")
    if format == 'json':
        click.echo(json.dumps([w.to_dict() for w in workflows], indent=4, cls=UUIDEncoder))


autoretouch_cli.add_command(login)
autoretouch_cli.add_command(logout)
autoretouch_cli.add_command(organizations)
autoretouch_cli.add_command(organization)
config.add_command(config_get)
config.add_command(config_set)
autoretouch_cli.add_command(config)
autoretouch_cli.add_command(upload)
autoretouch_cli.add_command(balance)
autoretouch_cli.add_command(process)
autoretouch_cli.add_command(workflows)
