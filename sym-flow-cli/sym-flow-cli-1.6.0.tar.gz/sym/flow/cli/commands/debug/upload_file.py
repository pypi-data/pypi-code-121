import click

from ...helpers.debug import do_upload_file


@click.command(short_help="Share a file with Sym")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def upload_file(file: click.Path) -> None:
    """Share the contents of FILE with Sym."""

    click.echo("Uploading...")
    txid = do_upload_file(str(file))
    click.secho(f"Your file was shared with Sym!", fg="green")
    click.secho(f"Transaction ID: {txid}", fg="black", bold=True)
