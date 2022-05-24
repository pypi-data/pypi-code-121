#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#
"""Download and save files command."""

from pathlib import Path

import requests
from rich.progress import Progress

from aos_prov.utils.common import DOWNLOADS_PATH
from aos_prov.utils.errors import AosProvError

_SAVE_CHUNK = 8192


def _create_downloads_directory():
    Path(DOWNLOADS_PATH).mkdir(parents=True, exist_ok=True)


def download_and_save_file(download_url: str, save_path: Path, force_overwrite: bool = False) -> None:
    """Download and save file.

    Args:
         download_url (str): URL to download
         save_path (Path): URL to download
         force_overwrite (bool): URL to download

    Raises:
        AosProvError: If file exists and force_overwrite is false.
    """
    _create_downloads_directory()

    if save_path.exists() and not force_overwrite:
        raise AosProvError('Destination file already exist.')

    with open(save_path, 'wb') as save_context:
        response = requests.get(download_url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            save_context.write(response.content)
            return

        with Progress() as progress:
            task_id = progress.add_task('[cyan]Downloading...', total=int(total_length))
            for received_data in response.iter_content(chunk_size=_SAVE_CHUNK):
                progress.update(task_id, advance=len(received_data))
                save_context.write(received_data)
