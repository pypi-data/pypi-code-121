import logging
import sys
import click
import json
import os

from .version import __version__
from . import core
from . import settings
from . import utilities

logging.basicConfig(format=utilities.FORMAT_STRING, level=logging.INFO)
log = logging.getLogger(__name__)

_session = core.Session()


def project(func):
    return click.option("--project", default="S", help="Project", show_default=True)(
        func
    )


def component_type(func):
    return click.option(
        "--component-type",
        help="Code for the type of component to query. Run list-component-types to find what types are available.",
        show_default=True,
    )(func)


def component_code(func):
    return click.option(
        "--component", help="Component code or component serial number", required=True
    )(func)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__)
@click.option(
    "--accessCode1",
    prompt=not (bool(settings.ITKDB_ACCESS_CODE1)),
    default=settings.ITKDB_ACCESS_CODE1,
    show_default=True,
)
@click.option(
    "--accessCode2",
    prompt=not (bool(settings.ITKDB_ACCESS_CODE2)),
    default=settings.ITKDB_ACCESS_CODE2,
    show_default=True,
)
@click.option("--auth-url", default=settings.ITKDB_AUTH_URL, show_default=True)
@click.option("--site-url", default=settings.ITKDB_SITE_URL, show_default=True)
@click.option(
    "--save-auth",
    help="Filename to save authenticated user to for persistence between requests",
    default=".auth",
)
def itkdb(accesscode1, accesscode2, auth_url, site_url, save_auth):
    global _session
    _session.prefix_url = site_url
    _session.user._prefix_url = auth_url
    _session.user._accessCode1 = accesscode1
    _session.user._accessCode2 = accesscode2
    _session.user._save_auth = save_auth
    _session.user._load()


@itkdb.command()
def authenticate():
    _session.user.authenticate()
    click.echo(
        "You have signed in as {}. Your token expires in {}s.".format(
            _session.user.name, _session.user.expires_in
        )
    )


@itkdb.command()
def stats():
    click.echo(
        json.dumps(
            _session.get("getItkpdOverallStatistics").json()["statistics"], indent=2
        )
    )
    sys.exit(0)


@itkdb.command()
def list_institutes():
    click.echo(
        json.dumps(_session.get("listInstitutions").json()["pageItemList"], indent=2)
    )
    sys.exit(0)


# NB: list_component_type_codes is the same as this, but use jq
#  $ itkdb list-component-types --project P | jq '[.[] | {code: .code, name: .name}]'
@itkdb.command()
@project
def list_component_types(project):
    data = {"project": project}
    click.echo(
        json.dumps(
            _session.get("listComponentTypes", json=data).json()["pageItemList"],
            indent=2,
        )
    )
    sys.exit(0)


@itkdb.command()
@project
@component_type
def list_components(project, component_type):
    data = {"project": project}
    if component_type:
        data.update({"componentType": component_type})
    click.echo(
        json.dumps(
            _session.get("listComponents", json=data).json()["itemList"], indent=2
        )
    )
    sys.exit(0)


# currently broken FYI
@itkdb.command()
def list_all_attachments():
    click.echo(
        json.dumps(
            _session.get("uu-app-binarystore/listBinaries").json()["itemList"], indent=2
        )
    )
    sys.exit(0)


@itkdb.command()
def list_projects():
    click.echo(json.dumps(_session.get("listProjects").json()["itemList"], indent=2))
    sys.exit(0)


@itkdb.command()
@project
@component_type
def list_test_types(project, component_type):
    data = {"project": project, "componentType": component_type}
    click.echo(
        json.dumps(
            _session.get("listTestTypes", json=data).json()["pageItemList"], indent=2
        )
    )
    sys.exit(0)


@itkdb.command()
@component_code
def get_component_info(component):
    data = {"component": component}
    click.echo(json.dumps(_session.get("getComponent", json=data).json(), indent=2))
    sys.exit(0)


@itkdb.command()
@project
def summary(project):
    header_str = "====={0:^100s}====="
    click.echo(header_str.format("Institutes"))
    institutes = _session.get("listInstitutions").json()["pageItemList"]
    for institute in institutes:
        click.echo("{name} ({code})".format(**institute))

    click.echo(header_str.format("Strip component types"))
    componentTypes = _session.get(
        "listComponentTypes", json={"project": project}
    ).json()["pageItemList"]

    for componentType in componentTypes:
        click.echo("{name} ({code}) {state}".format(**componentType))

    click.echo(header_str.format("Test types by component"))
    for componentType in componentTypes:
        click.echo("Test types for {code}".format(**componentType))
        test_types = _session.get(
            "listTestTypes",
            json={"project": project, "componentType": componentType["code"]},
        ).json()["pageItemList"]
        for test_type in test_types:
            click.echo("  {name} ({code}) {state}".format(**test_type))


@itkdb.command()
@component_code
@click.option("--title", help="Short description", required=True)
@click.option("-d", "--description", help="Description of attachment", required=True)
@click.option(
    "-f", "--file", help="File to attach", required=True, type=click.Path(exists=True)
)
@click.option("--filename", help="If specified, override filename of attachment")
@click.option(
    "--file-type", help="The type of the file being uploaded", default="text/plain"
)
def add_attachment(component, title, description, file, filename, file_type):
    filename = filename if filename else os.path.basename(file)

    data = {
        "component": component,
        "title": title,
        "description": description,
        "type": "file",
        "url": filename,
    }
    attachment = {"data": (filename, open(file, "rb"), file_type)}
    click.echo(
        json.dumps(
            _session.post(
                "createComponentAttachment", data=data, files=attachment
            ).json(),
            indent=2,
        )
    )
    sys.exit(0)


@itkdb.command()
@component_code
@click.option("-m", "--message", help="Comment to add to component", required=True)
def add_comment(component, message):
    data = {"component": component, "comments": [message]}
    click.echo(
        json.dumps(_session.post("createComponentComment", json=data).json(), indent=2)
    )
    sys.exit(0)
