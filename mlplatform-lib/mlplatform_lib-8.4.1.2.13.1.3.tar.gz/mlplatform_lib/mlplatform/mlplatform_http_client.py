from dataclasses import dataclass
from enum import Enum
import requests
from typing import Optional, Dict, List, Union
from pathlib import Path
from mlplatform_lib.dataclass.model import ModelInfoDto
from datetime import datetime
from mlplatform_lib.utils.dataclass_utils import to_dict, from_dict
from mlplatform_lib.auth import Auth
import os
import tarfile


MLPLATFORM_TIMSTAMP_FORMAT = "%Y.%m.%d %H:%M:%S"


class MlPlatformRequestException(Exception):
    status_code = 200

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class MlPlatformRequestType(Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class MlPlatformUserAuth:
    project_id: str
    user_id: str
    authorization: str
    authorization_type: str


@dataclass
class MlPlatformRequestResult:
    data: Optional[Union[Dict, List[Dict], bytes]]
    status_code: Optional[int]


class MlPlatformHttpClient:
    def __init__(self, mlplatform_addr, api_client):
        self.base_url = mlplatform_addr
        self.api_client = api_client

    def send_request(
        self,
        service: str,
        rest: Optional[dict],
        query: Optional[dict],
        data: Union[Optional[dict], Path],
        request_type: MlPlatformRequestType,
    ) -> MlPlatformRequestResult:
        auth = Auth(api_client=self.api_client)

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth.authorization,
            "userId": auth.userId,
            "projectId": auth.projectId,
            "authorizationType": auth.authorizationType,
        }

        if rest is None:
            rest = {}

        if query is None:
            query = {}

        if data is None:
            data = {}

        url = self.base_url
        for key, val in rest.items():
            url = url + "/" + str(key) + "/" + str(val)
        if service != "" and service is not None:
            url = url + "/" + service

        if len(query) != 0:
            url += "?"
            for idx, (key, val) in enumerate(query.items()):
                if idx != 0:
                    url += "&"
                url = url + str(key) + "=" + str(val)

        if request_type == MlPlatformRequestType.READ:
            response = requests.get(url, headers=headers, json=data, verify=False)
        elif request_type == MlPlatformRequestType.CREATE:
            if isinstance(data, Path):
                headers.pop("Content-Type", None)
                response = requests.post(url, headers=headers, files={"file": open(data, "rb")})
            else:
                response = requests.post(url, headers=headers, json=data, verify=False)
        elif request_type == MlPlatformRequestType.UPDATE:
            response = requests.put(url, headers=headers, json=data, verify=False)
        elif request_type == MlPlatformRequestType.DELETE:
            response = requests.delete(url, headers=headers, json=data, verify=False)
        else:
            raise MlPlatformRequestException(status_code=405, message=f"{request_type} method not allowed.")

        if response.status_code == 200:
            return MlPlatformRequestResult(response.json(), response.status_code)
        else:
            print(
                (
                    f"{service} {request_type.value} failed\n"
                    f"status_code: {response.status_code}.\n"
                    f"reason: {response.text}\n"
                )
            )
            raise MlPlatformRequestException(response.content.decode(), response.status_code)

    def upload_inference_csv(self, experiment_id: int, inference_id: int, inference_csv_path: str) -> None:
        self.send_request(
            "file",
            {"experiments": experiment_id, "inferences": inference_id},
            {},
            Path(inference_csv_path),
            MlPlatformRequestType.CREATE,
        )

    def insert_model_info(
        self, experiment_id: int, train_id: int, model_id: int, model_info: ModelInfoDto
    ) -> ModelInfoDto:
        model_info.finished_time = datetime.now().strftime(MLPLATFORM_TIMSTAMP_FORMAT)

        result = self.send_request(
            "info",
            {"experiments": experiment_id, "trains": train_id, "models": model_id},
            {},
            to_dict(model_info),
            MlPlatformRequestType.CREATE,
        )
        return from_dict(ModelInfoDto, result.data)

    def upload_model(self, experiment_id: int, train_id: int, model_id: int, model_path: str):
        is_dir = os.path.isdir(model_path)
        if is_dir:
            tar_path = os.path.join(model_path, os.path.basename(model_path) + ".tar.gz")
            with tarfile.open(tar_path, "w:gz") as tar:
                for file in os.listdir(model_path):
                    tar.add(os.path.join(model_path, file), arcname=file)
        else:
            tar_path = os.path.join(os.path.dirname(model_path), "model.tar.gz")
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(model_path, arcname=os.path.basename(model_path))

        self.send_request(
            "upload",
            {"experiments": experiment_id, "trains": train_id, "models": model_id},
            {},
            Path(tar_path),
            MlPlatformRequestType.CREATE,
        )

        os.remove(tar_path)
