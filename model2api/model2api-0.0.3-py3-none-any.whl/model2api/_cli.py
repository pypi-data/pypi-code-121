"""Command line interface."""

import os
import sys

import typer

cli = typer.Typer()


@cli.command()
def launch_api(
    predictor: str,
    port: int = typer.Option(8080, "--port", "-p"),
    host: str = typer.Option("0.0.0.0", "--host", "-h"),
) -> None:
    """Start a HTTP API server for the opyrator.

    This will launch a FastAPI server based on the OpenAPI standard and with an automatic interactive documentation.
    """

    # Add the current working directory to the sys path
    # This is required to resolve the opyrator path
    sys.path.append(os.getcwd())

    from model2api.api.fastapi_app import launch_api  # type: ignore

    launch_api(predictor, port, host)
