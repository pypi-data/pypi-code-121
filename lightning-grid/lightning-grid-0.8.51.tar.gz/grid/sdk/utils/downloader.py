from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import requests
from tqdm import tqdm


@dataclass
class DownloadableObject:
    """Object that can be downloaded from an URL into a local path."""
    url: str
    download_path: str
    filename: str
    downloaded: bool = False


class Downloader:
    @staticmethod
    def single_file_download(
        obj: DownloadableObject,
        destination: Union[str, Path],
        progress_bar: Optional[tqdm] = None,
        chunk_size: int = 4096,  # golang bufio defaultBufSize
    ):
        """Downloads a single object to the filesystem.

        This function will produce one progress bar:
            1. Download progress of the file in bytes

        Parameters
        ----------
        obj : DownloadableObject
            The object to download.
        destination : Union[str, Path]
            Path in the filesystem to place download.
        progress_bar : Optional[tqdm], optional
            Existing progress bar, by default None.
            If None, a progress bar will be created.
            Shows bytes downloaded.
        chunk_size : int, optional
            We stream the file to disk in this chunk size (in bytes).
            By default 4096 bytes (4 kibibytes).
        """
        # make the destination directory if necessary
        destination = Path(destination) / Path(obj.download_path) / Path(obj.filename)
        Path(destination).parent.mkdir(parents=True, exist_ok=True)

        # request file to download
        file_download = requests.get(obj.url, allow_redirects=True, stream=True)
        file_download_size = int(file_download.headers.get("content-length", 0))

        # initialize progress bar
        if progress_bar is None:
            progress_bar = tqdm(unit="B", unit_scale=True)
        progress_bar.reset()
        progress_bar.set_description(desc=str(Path(obj.download_path) / obj.filename))
        progress_bar.total = file_download_size

        # start download
        with open(destination, 'wb') as file:
            for chunk in file_download.iter_content(chunk_size=chunk_size):
                if chunk:
                    progress_bar.update(file.write(chunk))
        progress_bar.refresh()

        # Mark object as downloaded
        obj.downloaded = True

    @staticmethod
    def multi_file_download(
        downloadable_objects: List[DownloadableObject],
        destination: str,
        description: str = "files downloaded",
        unit: str = "file",
        chunk_size: int = 4096,  # golang bufio defaultBufSize
        position: int = 0,
    ):
        """
        Downloads multiple files to the filesystem.

        This function will produce two progress bars:
            1. Progress of all files in `downloadable_objects`
            2. Download progress for a single file in bytes

        Attributes
        ----------
        downloadable_objects : List[DownloadableObject]
            List of objects containing URL and file system information.
        destination : str
            Path to place all downloads.
        description : str, optional
            String to display on the progress bar, by default "files downloaded".
        unt : str, optional
            Unit of the object we are downloading, by default "file".
            Some files have special names, like "artifact" or "log".
        chunk_size : int, optional
            We stream the file to disk in this chunk size (in bytes).
            By default 4096 bytes (4 kibibytes).
        position : int, optional
            The tqdm position argument, by default 0.
            Sets the order for multiple progress bars.
        """
        # It would be nice to keep the input as an iterator
        # but it could make the progress bars ugly.
        # You can't take the len() of a generator!
        downloadable_objects = list(downloadable_objects)

        total_progress = tqdm(downloadable_objects, unit=unit, position=position, desc=description, leave=False)
        file_progress = tqdm(unit="B", unit_scale=True, position=position + 1, leave=False)
        for obj in total_progress:
            obj: DownloadableObject

            # Download file to path
            # TODO figure out why concurrency was taken out in a previous commit
            Downloader.single_file_download(obj, destination, file_progress, chunk_size)

        file_progress.close()
        total_progress.close()
