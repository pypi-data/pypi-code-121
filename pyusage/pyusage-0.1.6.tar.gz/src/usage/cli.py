import os
from typing import Generator, Iterable, Optional

import click
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from termcolor import colored

from .decorators import collect
from .session import get_or_create_session


@click.group()
def usage():
    pass


@usage.command()
@click.argument("package")
@collect
def download(package: str, path: str = "sessions.json"):
    """Download usage data from a package."""
    if os.path.exists(path):
        _warn_file_overwrite(path)
        # TODO: This is a hack to empty the file.
        with open(path, "w", encoding="utf-8"):
            pass

    _print_download_start(package, path)
    session = get_or_create_session()
    content_stream, size = session.client.download_sessions(package)
    with open(path, "ab") as file:
        for chunk in _progress_bar(content_stream, size=size):
            file.write(chunk)


def _warn_file_overwrite(path: str) -> None:
    print(
        colored("WARNING:", attrs=["bold"], color="red"),
        colored(path, color="yellow"),
        "will be overwritten",
    )


def _print_download_start(package: str, path: str) -> None:
    print(
        "Downloading",
        colored(package, color="cyan"),
        "usage data to",
        colored(path, color="yellow"),
    )


def _progress_bar(
    iterable: Iterable[bytes], *, size: Optional[int]
) -> Generator[bytes, None, None]:
    columns = (
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TextColumn("eta"),
        TimeRemainingColumn(),
    )
    progress = Progress(*columns, refresh_per_second=30, transient=False)
    task_id = progress.add_task(" " * 2, total=size)
    with progress:
        for chunk in iterable:
            yield chunk
            progress.update(task_id, advance=len(chunk))
