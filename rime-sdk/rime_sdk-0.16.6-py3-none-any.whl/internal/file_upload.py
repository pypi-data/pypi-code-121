"""Library providing a module for file services."""
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Text

import grpc
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from rime_sdk.protos.file_upload.file_upload_pb2 import (
    GetDatasetFileUploadURLRequest,
    GetModelDirectoryUploadURLsRequest,
)
from rime_sdk.protos.file_upload.file_upload_pb2_grpc import FileUploadStub


def _now_str() -> str:
    """Generate a date string for the current time."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")


class FileUploadModule:
    """A module that implements file uploading using a FileUploadStub."""

    def __init__(self, file_upload_client: FileUploadStub):
        """Create a FileUploadModule for the `file_upload_client`."""
        self._file_upload_client = file_upload_client

    def upload_dataset_file(self, file_path: Path) -> str:
        """Upload dataset file ``file_path`` to RIME's blobstore via a FileUploadStub.

        The uploaded file is placed within the blobstore using its file name.

        Args:
            file_path: Path
                Path to the file to be uploaded to RIME's blob store.

        Returns:
            A reference to the uploaded file's location in the blob store. This
            reference can be used to refer to that object when writing RIME configs.

        Raises:
            FileNotFoundError:
                If the path ``file_path`` does not exist.
            IOError:
                If ``file_path`` is not a file.
            ValueError:
                If there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"path '{file_path}' does not exist")
        if not file_path.is_file():
            raise IOError(f"path '{file_path}' is not a file")

        file_size = file_path.stat().st_size

        file_name = file_path.name
        req = GetDatasetFileUploadURLRequest(file_name=file_name)
        try:
            resp = self._file_upload_client.GetDatasetFileUploadURL(request=req)
            self._impose_size_constraint(file_size, resp.upload_limit)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)
        self._upload_object(file_path, resp.upload_url)
        self._upload_string(f"Upload complete: {_now_str()}", resp.done_file_upload_url)
        return resp.destination_url

    def upload_model_directory(
        self, dir_path: Path, upload_hidden: bool = False
    ) -> str:
        """Upload model directory ``dir_path`` to RIME's blobstore via a FileUploadStub.

        All files contained within ``dir_path`` and its subdirectories are uploaded
        according to their relative paths within ``dir_path``.  However, if
        upload_hidden is False, all hidden files and subdirectories beginning with
        a '.' are not uploaded.

        Args:
            dir_path: Path
                Path to the directory to be uploaded to RIME's blob store.
            upload_hidden: bool = False
                Whether or not to upload hidden files or subdirectories
                (ie. those beginning with a '.').

        Returns:
            A reference to the uploaded directory's location in the blob store. This
            reference can be used to refer to that object when writing RIME configs.

        Raises:
            FileNotFoundError:
                If the directory ``dir_path`` does not exist.
            IOError:
                If ``dir_path`` is not a directory or contains no files.
            ValueError:
                If there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``dir_path`` to RIME's blob store.
        """
        if not dir_path.exists():
            raise FileNotFoundError(f"path '{dir_path}' does not exist")
        if not dir_path.is_dir():
            raise IOError(f"path '{dir_path}' is not a directory")
        sub_paths = (
            dir_path.rglob("*")
            if upload_hidden
            else filter(
                lambda path: not any(
                    (part for part in path.parts if part.startswith("."))
                ),
                dir_path.rglob("*"),
            )
        )
        rel_paths: List[Text] = []
        total_size: int = 0
        for file_path in sub_paths:
            if file_path.is_file():
                total_size += file_path.stat().st_size
                rel_paths.append(str(file_path.relative_to(dir_path)))
        if len(rel_paths) == 0:
            raise IOError(f"directory '{dir_path}' is empty")
        req = GetModelDirectoryUploadURLsRequest(
            directory_name=dir_path.name, relative_file_paths=rel_paths
        )
        try:
            resp = self._file_upload_client.GetModelDirectoryUploadURLs(request=req)
            self._impose_size_constraint(total_size, resp.upload_limit)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)
        for rel_path in resp.upload_path_map:
            file_path = dir_path / rel_path
            self._upload_object(file_path, resp.upload_path_map[rel_path])
        self._upload_string(f"Upload complete: {_now_str()}", resp.done_file_upload_url)
        return resp.destination_url

    def _upload_object(self, file_path: Path, upload_url: str) -> None:
        """Upload the `file_path` to the location at `upload_url` via a PUT request."""
        file_size = file_path.stat().st_size
        with open(file_path, "rb") as f, self._get_requests_session() as session:
            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Uploading {file_path}",
            ) as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                http_response = session.put(url=upload_url, data=wrapped_file)
                if http_response.status_code != 200:
                    raise ValueError(
                        f"upload of '{file_path}' failed with "
                        + f"{http_response.status_code}: {http_response.reason}"
                    )

    def _get_requests_session(self) -> requests.Session:
        """Create request session for submitting HTTPS requests with retries."""
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=5)
        session.mount("https://", adapter)
        return session

    def _impose_size_constraint(self, size: int, upload_limit: int) -> None:
        if (upload_limit != 0) and (size > upload_limit):
            raise ValueError(
                "Input is too large to be uploaded. Maximum size permitted "
                + f"is {upload_limit / (10 ** 6)}MB. "
                + f"Input size given is {size / (10 ** 6)}MB"
            )

    def _upload_string(self, file_contents: str, upload_url: str) -> None:
        """Upload `file_contents` to the location at `upload_url` via a PUT request."""
        with self._get_requests_session() as session:
            http_response = session.put(url=upload_url, data=file_contents)
            if http_response.status_code != 200:
                raise ValueError(
                    "upload of raw string file failed with "
                    + f"{http_response.status_code}: {http_response.reason}"
                )
