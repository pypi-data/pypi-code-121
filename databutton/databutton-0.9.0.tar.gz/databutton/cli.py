# !/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import tarfile
import webbrowser
from uuid import uuid4

import click
import requests
from yaspin import yaspin

from databutton.utils import (
    create_databutton_config,
    get_auth_token,
    get_databutton_config,
    get_databutton_login_info,
    upload_archive,
)
from databutton.utils.deploy import create_archive, listen_to_build

from .__init__ import __version__

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}  #: a mapping of `verbose` option counts to logging levels


# Change the options to below to suit the actual options for your task (or
# tasks).


@click.group()
@click.option("--verbose", "-v", count=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, verbose: int):
    ctx.ensure_object(dict)
    """Run databutton."""
    # Use the verbosity count to determine the logging level...
    if verbose > 0:
        logging.basicConfig(
            level=LOGGING_LEVELS[verbose]
            if verbose in LOGGING_LEVELS
            else logging.DEBUG
        )
    ctx.obj["VERBOSE"] = verbose


@cli.command()
def version():
    """Get the library version."""
    click.echo(click.style(f"{__version__}", bold=True))


@cli.command()
@click.option(
    "--template",
    default="sales-forecasting",
    type=click.Choice(["sales-forecasting", "reddit-tinder"]),
    prompt="Select a template",
)
@click.option("--name", default="my-databutton-app", prompt="Name of the app")
def create(template, name):
    """Create an application with a template"""
    click.echo(click.style(f"You selected {template}"))

    # Fetch repository
    os.mkdir(name)
    click.echo("Download template...")
    res = requests.get(
        f"https://storage.googleapis.com/databutton-app-templates/{template}.tar.gz",
        stream=True,
    )
    if res.ok:
        tmpname = f"/tmp/databutton-{template}.tar.gz"
        with open(tmpname, "wb") as f:
            f.write(res.raw.read())
        tar_obj = tarfile.open(tmpname)
        tar_obj.extractall(name)
        os.remove(tmpname)
        click.echo()
        click.echo(click.style(f"Successfully created {name}", fg="green"))
        click.echo()
        click.echo(click.style(f"cd into the folder (cd {name}) and start hacking!"))
        click.echo(
            click.style(
                "Use your favorite environment setup to install requirements with"
            )
        )
        click.echo()
        click.echo(click.style("pip install -r requirements.txt", fg="green"))
        click.echo()
        click.echo(
            click.style(
                "write `databutton dev` and make the data app yours!", fg="green"
            )
        )
        click.echo()
        click.echo()

    else:
        click.echo(click.style(f"Error, could not get template {template}"))
        quit(1)


@cli.command()
@click.option("--open", "-o", default=False, type=bool, show_default=True, is_flag=True)
def dev(open=False):
    """Run the development server of databutton"""

    import sys

    import uvicorn
    from uvicorn.supervisors import ChangeReload

    dir_path = os.path.dirname(os.path.realpath(__file__))
    app_dir = os.path.join(dir_path, "server")
    sys.path.insert(0, app_dir)
    # For some reason, when CTRL+C you get an ugly error message.
    # This is related to a uvicorn issue: https://github.com/encode/uvicorn/issues/1160
    config = uvicorn.Config(
        "server:app",
        reload=True,
        reload_excludes=".databutton/**/*.py",
        log_level="error",
    )
    server = uvicorn.Server(config=config)
    server.force_exit = True
    sock = config.bind_socket()
    supervisor = ChangeReload(config, target=server.run, sockets=[sock])
    if open:
        import webbrowser

        webbrowser.open("http://localhost:8000")
    supervisor.run()


@cli.command()
def login():
    """Login to databutton"""
    import uvicorn

    dir_path = os.path.dirname(os.path.realpath(__file__))
    app_dir = os.path.join(dir_path, "auth")
    click.echo(click.style("Opening browser to authenticate"))
    click.echo()
    click.echo(click.style("Exit this process with ctrl+c"))
    click.echo()
    login_url = "https://next.databutton.com/login?next=http://localhost:8008"
    webbrowser.open_new_tab(login_url)
    uvicorn.run(
        "server:app", app_dir=app_dir, reload=False, log_level="error", port=8008
    )


@cli.command()
@click.pass_context
def deploy(ctx: click.Context):
    """Deploy to databutton"""

    def get_auth(retries=1):
        if retries == 0:
            return None
        try:
            login_info = get_databutton_login_info()
            if login_info is None:
                raise Exception()
            return login_info
        except Exception:
            click.echo(click.style("No login info found, logging in first..."))
            click.echo()
            ctx.invoke(login)
            click.echo()
            return get_auth(retries - 1)

    def get_config():
        try:
            config = get_databutton_config()
            return config
        except Exception:
            click.echo(
                click.style("No databutton.json config found, creating a new one...")
            )
            ctx.invoke(create_databutton_project)
            return get_config()

    if get_auth() is None:  # Make sure the user has a valid auth thingy
        click.echo(click.style("Could not authenticate. Try again.", fg="red"))
        quit()
    config = get_config()
    deployment_id = str(uuid4())

    click.echo()
    click.echo(click.style(f"=== Deploying to {config.name}", fg="green"))
    ctx.invoke(build)
    click.echo(click.style("i packaging components...", fg="cyan"))
    archive_path = create_archive(deployment_id, source_dir=os.curdir, config=config)
    click.echo(click.style("i done packaging components", fg="green"))
    click.echo(click.style("i uploading components", fg="cyan"))
    upload_archive(config, deployment_id, archive_path)
    click.echo(click.style("i finished uploading components", fg="green"))
    click.echo(click.style("i cleaning up", fg="cyan"))
    # Clean up artifact
    os.remove(archive_path)

    click.echo(
        click.style(
            "i waiting for deployment to be ready, this can take some time..", fg="cyan"
        )
    )
    with yaspin(text=click.style("i deploying...", fg="cyan"), color="cyan"):
        build_id, status = listen_to_build(deployment_id)
    if status == "SUCCESS":
        click.echo(click.style("✅ Done!", fg="green"))
        click.echo()
        styled_url = click.style(
            f"https://next.databutton.com/projects/{config.uid}", fg="cyan"
        )
        click.echo(f"You can now to go {styled_url}")
        click.echo()
    elif status == "FAILURE":
        click.echo(click.style("❌ Error deploying...", fg="red"))
        click.echo()
    log_url_response = requests.get(
        "https://europe-west1-databutton.cloudfunctions.net/get_cloud_build_logs",
        params={"build_id": build_id},
        headers={"Authorization": f"Bearer {get_auth_token()}"},
    )
    log_url = log_url_response.json()["signed_url"]
    click.echo(click.style(f"⚙️ You can see build logs at {log_url}"))
    click.echo()


@cli.command()
def build():
    click.echo(click.style("i building project", fg="cyan"))
    from databutton.utils.build import generate_components

    click.echo(click.style("i generating components", fg="cyan"))
    artifacts = generate_components()
    click.echo(click.style("i finished building project in .databutton", fg="green"))
    return artifacts


@cli.command()
def serve():
    click.echo(click.style("=== Serving"))
    import uvicorn

    dir_path = os.path.dirname(os.path.realpath(__file__))
    app_dir = os.path.join(dir_path, "server")
    port = os.environ["PORT"] if "PORT" in os.environ else 8000
    uvicorn.run(
        "prod:app", app_dir=app_dir, reload=False, port=int(port), host="0.0.0.0"
    )


@cli.command("init")
@click.option("--name", default=os.path.basename(os.getcwd()), prompt=True)
def create_databutton_project(name: str):
    if os.path.exists("databutton.json"):
        click.secho(
            "There's already a databutton.json file in this repo, delete it to create a new project."
        )
        exit(1)
    token = get_auth_token()
    res = requests.post(
        "https://europe-west1-databutton.cloudfunctions.net/createOrUpdateProject",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    res_json = res.json()
    new_id = res_json["id"]
    config = create_databutton_config(name, new_id)
    click.echo(click.style(f"i creating project {name}", fg="cyan"))
    click.echo(click.style("i writing config to databutton.json", fg="cyan"))
    click.echo(
        click.style(
            f"✅ created project with name {name}",
            fg="green",
        )
    )
    click.echo()
    styled_url = click.style(
        f"https://next.databutton.com/projects/{new_id}", fg="cyan"
    )
    click.echo(
        f"You can check out your project on \n\n\t{styled_url} \n\nafter you have deployed with databutton deploy."
    )
    return config
