import typer

from benchling_sdk.apps.cli import apps_cli

cli = typer.Typer()
cli.add_typer(
    apps_cli,
    name="app",
    help="Benchling apps are portable and transferable integrations administered within Benchling.",
)

if __name__ == "__main__":
    cli()
