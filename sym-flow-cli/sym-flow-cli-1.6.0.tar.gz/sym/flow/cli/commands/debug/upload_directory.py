import click

from ...helpers.debug import do_upload_directory


@click.command(short_help="Share a directory with Sym")
@click.argument("dir", type=click.Path(exists=True, file_okay=False))
def upload_directory(dir: click.Path) -> None:
    """Share the contents of DIR with Sym."""

    click.echo("Archiving and uploading...")
    txid = do_upload_directory(str(dir))
    click.secho(f"Your directory was shared with Sym!", fg="green")
    click.secho(f"Transaction ID: {txid}", fg="black", bold=True)
