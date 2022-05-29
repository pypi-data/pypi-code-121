from veet.commands import veet, typer
import os


@veet.command(name="os:env")
def handle(env: str):
    """
    Get value env
    """
    typer.echo(os.getenv(env))