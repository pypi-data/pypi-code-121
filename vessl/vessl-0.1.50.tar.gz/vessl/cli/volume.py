import os
from urllib.parse import urlparse

import click

from vessl.cli._base import VesslGroup, vessl_argument, vessl_option
from vessl.cli._util import generic_prompter, print_volume_files
from vessl.util.exception import InvalidVolumeFileError
from vessl.volume import copy_volume_file, delete_volume_file, list_volume_files


@click.command(name="volume", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=generic_prompter("Volume ID", click.INT),
)
@click.option("-p", "--path", type=click.Path(), default="", help="Defaults to root.")
@click.option("-r", "--recursive", is_flag=True)
def list(id: int, path: str, recursive: bool):
    files = list_volume_files(
        volume_id=id,
        path=path,
        need_download_url=False,
        recursive=recursive,
    )
    print_volume_files(files)


@cli.vessl_command()
@vessl_argument(
    "id",
    type=click.INT,
    required=True,
    prompter=generic_prompter("Volume ID", click.INT),
)
@click.option("-p", "--path", type=click.Path(), required=True)
def delete(id: int, path: str):
    delete_volume_file(volume_id=id, path=path)
    print(f"Deleted {id}.")


@cli.vessl_command()
@vessl_option(
    "--source-id",
    type=click.INT,
    prompter=generic_prompter("Source volume ID", click.INT),
    help="If not specified, source is assumed to be local.",
)
@vessl_option(
    "--source-path",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Source path"),
)
@vessl_option(
    "--dest-id",
    type=click.INT,
    prompter=generic_prompter("Destination volume ID", click.INT),
    help="If not specified, destination is assumed to be local.",
)
@vessl_option(
    "--dest-path",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Destination path"),
)
def copy(
    source_id: int, source_path: str, dest_id: int, dest_path: str,
):
    copy_volume_file(
        source_volume_id=source_id,
        source_path=source_path,
        dest_volume_id=dest_id,
        dest_path=dest_path,
    )


def parse_volume_url(volume_url: str, raise_if_not_exists: bool = False):
    if volume_url.startswith("sv://"):
        u = urlparse(volume_url)
        volume_id = int(u.netloc.split(":", 1)[0])
        path = u.path.lstrip("/")
        return volume_id, path

    path = os.path.abspath(volume_url)
    if not os.path.exists(path) and raise_if_not_exists:
        raise InvalidVolumeFileError(f"No such file: {volume_url}")

    return None, path


@cli.vessl_command(hidden=True)
@click.argument(
    "source",
    type=click.STRING,
    required=True,
)
@click.argument(
    "dest",
    type=click.STRING,
    required=True,
)
def cp(source: str, dest: str):
    """Volume copy method used in backend"""

    source_id, source_path = parse_volume_url(source, raise_if_not_exists=True)
    dest_id, dest_path = parse_volume_url(dest)

    copy_volume_file(
        source_volume_id=source_id,
        source_path=source_path,
        dest_volume_id=dest_id,
        dest_path=dest_path,
    )
