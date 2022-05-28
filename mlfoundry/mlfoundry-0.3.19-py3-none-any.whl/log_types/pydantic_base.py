import os
import posixpath
import tempfile
import time
import typing

from mlflow.entities import RunLog
from mlflow.tracking import MlflowClient
from mlflow.utils.file_utils import download_file_using_http_uri
from pydantic import BaseModel

from mlfoundry.exceptions import MlFoundryException


class PydanticBase(BaseModel):
    # I can make this a property,
    # but <3.9, it is difficult to access
    # property from classmethod
    @staticmethod
    def get_log_type() -> str:
        raise NotImplementedError()

    def to_run_log(
        self, key: str, step: int = 0, timestamp: typing.Optional[int] = None
    ) -> RunLog:
        timestamp = timestamp or int(time.time() * 1000)
        return RunLog(
            key=key,
            step=step,
            timestamp=timestamp,
            log_type=self.get_log_type(),
            value=self.json(),
        )

    def to_run_log_as_artifact(
        self,
        key: str,
        run_id: str,
        mlflow_client: MlflowClient,
        file_name: str,
        artifact_path: str,
        step: int = 0,
        timestamp: typing.Optional[int] = None,
    ) -> RunLog:
        with tempfile.TemporaryDirectory() as local_dir:
            file_path = os.path.join(local_dir, file_name)
            with open(file_path, "w") as fp:
                fp.write(self.json())

            mlflow_client.log_artifact(
                run_id=run_id, local_path=file_path, artifact_path=artifact_path
            )
        artifact_path = posixpath.join(artifact_path, file_name)
        timestamp = timestamp or int(time.time() * 1000)
        return RunLog(
            key=key,
            step=step,
            timestamp=timestamp,
            log_type=self.get_log_type(),
            artifact_path=artifact_path,
        )

    @classmethod
    def from_run_log(cls, run_log: RunLog):
        if run_log.log_type != cls.get_log_type():
            raise MlFoundryException(
                f"run_log.log_type {run_log.log_type} not matching with "
                f"{cls.__name__} log_type {cls.get_log_type()}"
            )
        value = run_log.value
        if value:
            return cls.parse_raw(value)

        artifact_signed_uri = run_log.artifact_signed_uri
        with tempfile.NamedTemporaryFile(mode="w") as file_path:
            download_file_using_http_uri(
                http_uri=artifact_signed_uri, download_path=file_path.name
            )
            return cls.parse_file(file_path.name)
