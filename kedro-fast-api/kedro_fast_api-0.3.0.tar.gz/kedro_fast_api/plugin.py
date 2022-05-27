import os

import click
from pathlib import Path
from kedro_fast_api.api_factory import ApiFactory
from kedro_fast_api.init_files import create_init_files
from kedro_fast_api.dockerfile_generator import create_dockerfile
from kedro.framework.startup import _get_project_metadata
from kedro.framework.session import KedroSession

""" Console script for extendable_base_dash.

Commands:
  run-api      Init API

ika run-api: Serves fast API
    Options:
    -p, --path Path to api_config.yml

"""

@click.group(name="FastAPI")
def commands():
    pass


@commands.group()
def fast_api(name="fast-api"):
    """Use fast api commands inside kedro project."""
    pass  # pragma: no cover

@fast_api.command()
@click.option("--path", "-p", "in_path",
              default="conf/api.yml",
              help="Path to config file")
@click.option("--workers", "-w", "workers",
              default=1,
              help="")
@click.option("--port", "-P", "port",
              default="8000",
              help="Port to run API")
def run(in_path, workers, port):
    """ Serves FastAPI"""
    try:
        api = ApiFactory(in_path)
        api.create_app_file()
        os.system(f'uvicorn app:app --host 0.0.0.0 --workers {workers} --port {port}')
        os.system('rm -rf app.py')
    except Exception as e:
        raise e

@fast_api.command()
def init():
    """
        This command will generate:

        A api_config.yml config file
        A catalog.yml file to save the predictor
        A new kedro pipeline (one node in one pipeline) with a predictor template.
    """
    try:
        project_path = Path.cwd()
        metadata = _get_project_metadata(project_path)
        session = KedroSession.create(metadata.package_name, project_path)
        context = session.load_context()
        create_init_files(context.package_name)
    except Exception as e:
        raise e

@fast_api.command()
def dockerfile():
    """
        This command will generate a dockerfile and a .dockerignore files
    """
    try:
        create_dockerfile()
    except Exception as e:
        raise e