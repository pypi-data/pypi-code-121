import os
from concurrent.futures import Future

from requests_futures.sessions import FuturesSession

from openapi_client import StorageFile
from vessl.util.file_transmission import (
    FileTransmissionHandler,
    FileTransmissionTracker,
)


class Downloader:
    @classmethod
    def download(
        cls,
        source_path: str,
        dest_path: str,
        *remote_files: StorageFile,
        quiet: bool = False,
    ):
        """Download volume files"""
        if not remote_files:
            return

        handler = FileTransmissionHandler(
            cls._download_future, action="download", quiet=quiet
        )
        if len(remote_files) == 1 and remote_files[0].path == source_path:
            handler.add_file(
                dest_path, remote_files[0].download_url.url, remote_files[0].size
            )
        else:
            dir_exists = os.path.exists(dest_path)
            for file in remote_files:
                if dir_exists:
                    # create subdirectory
                    dir_name = os.path.basename(os.path.dirname(file.path))
                    file_name = os.path.basename(file.path)
                    local_full_path = os.path.join(dest_path, dir_name, file_name)
                else:
                    local_full_path = os.path.join(
                        dest_path, os.path.basename(file.path)
                    )
                handler.add_file(local_full_path, file.download_url.url, file.size)

        handler.run()

    @classmethod
    def _download_future(
        cls,
        session: FuturesSession,
        full_path: str,
        url: str,
        tracker: FileTransmissionTracker,
    ) -> Future:
        return session.get(
            url, stream=True, hooks={"response": cls._download_hook(full_path, tracker)}
        )

    @staticmethod
    def _download_hook(full_path, tracker=None):
        def fn(resp, **kwargs):
            if not resp.ok:
                return

            dirname = os.path.dirname(full_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            with open(full_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if tracker:
                        tracker.increase_done_size(len(chunk))
                        tracker.print_progress()
                if tracker:
                    tracker.increase_done_count()

        return fn
