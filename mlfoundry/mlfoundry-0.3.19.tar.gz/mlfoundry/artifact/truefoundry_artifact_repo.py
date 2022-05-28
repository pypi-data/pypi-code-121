import os
import posixpath
import typing

from mlflow.entities import FileInfo
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.utils.file_utils import (
    download_file_using_http_uri,
    relative_path_to_artifact_path,
)
from mlflow.utils.rest_utils import cloud_storage_http_request

from mlfoundry.tracking.entities.artifact_credentials import ArtifactCredential
from mlfoundry.tracking.truefoundry_rest_store import TruefoundryRestStore


class TruefoundryArtifactRepository(ArtifactRepository):
    def __init__(self, artifact_uri, rest_store: TruefoundryRestStore):
        self.artifact_uri = artifact_uri
        super().__init__(artifact_uri)

        self.rest_store: TruefoundryRestStore = rest_store

    @staticmethod
    def _extract_run_id(artifact_uri) -> str:
        # artifact_uri will be something like,
        # s3://<BUCKET>/<PATH>/<EXP_ID>/<RUN_ID>/artifacts
        run_id = artifact_uri.rstrip("/").split("/")[-2]
        return run_id

    def list_artifacts(self, path=None) -> typing.List[FileInfo]:
        run_id = self._extract_run_id(self.artifact_uri)
        artifacts = self.rest_store.list_artifacts(run_id=run_id, path=path)
        return artifacts

    def _signed_uri_upload_file(
        self, artifact_credential: ArtifactCredential, local_file: str
    ):
        if os.stat(local_file).st_size == 0:
            with cloud_storage_http_request(
                "put",
                artifact_credential.signed_uri,
                data="",
            ) as response:
                response.raise_for_status()
        else:
            with open(local_file, "rb") as file:
                with cloud_storage_http_request(
                    "put",
                    artifact_credential.signed_uri,
                    data=file,
                ) as response:
                    response.raise_for_status()

    def log_artifacts(self, local_dir, artifact_path=None):
        dest_path = artifact_path or ""
        for (root, _, file_names) in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                rel_path = relative_path_to_artifact_path(rel_path)
                upload_path = posixpath.join(dest_path, rel_path)
            for file_name in file_names:
                local_file = os.path.join(root, file_name)
                self.log_artifact(local_file=local_file, artifact_path=upload_path)

    def log_artifact(self, local_file, artifact_path=None):
        dest_path = self.artifact_uri
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        dest_path = posixpath.join(dest_path, os.path.basename(local_file))
        artifact_credential = self.rest_store.get_artifact_write_credential(
            run_id=self._extract_run_id(self.artifact_uri), path=dest_path
        )
        self._signed_uri_upload_file(artifact_credential, local_file)

    def _download_file(self, remote_file_path: str, local_path: str):
        abs_remote_file_path = posixpath.join(self.artifact_uri, remote_file_path)
        artifact_credential = self.rest_store.get_artifact_read_credentials(
            run_id=self._extract_run_id(self.artifact_uri), path=abs_remote_file_path
        )
        download_file_using_http_uri(
            http_uri=artifact_credential.signed_uri, download_path=local_path
        )
