from mlplatform_lib.api_client import ApiClient, RunMode
from mlplatform_lib.dataclass.model import ModelInfoDto
from mlplatform_lib.hyperdata.hyperdata_api import HyperdataApi
from mlplatform_lib.mlplatform.mlplatform_http_client import MlPlatformHttpClient
from mlplatform_lib.mlplatform.mlplatform_local_checker import MlPlatformLocalChecker
from mlplatform_lib.dataclass.experiment import ExperimentDataObjectInfo
from mlplatform_lib.utils.dataclass_utils import from_dict
import os
from typing import List
from pathlib import Path


class MlPlatformApi:
    def __init__(self, api_client: ApiClient = None, local_mount_path="./tmp"):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.hyperdata_api = HyperdataApi(api_client=self.api_client)
        self.experiment_id = self.api_client.experiment_id
        self.train_id = self.api_client.train_id
        self.inference_id = self.api_client.inference_id
        if self.api_client.run_mode == RunMode.LOCAL:
            self.local_checker = MlPlatformLocalChecker(api_client=self.api_client)
            self.local_checker.run()
            self.train_do_id = self.local_checker.train_do_id
            self.train_data_object_info_list: List[ExperimentDataObjectInfo] = self.local_checker.train_data_object_info_list
            self.inference_do_id = self.local_checker.inference_do_id
            self.mount_path = local_mount_path
            Path(self.mount_path).mkdir(parents=True, exist_ok=True)
        if self.api_client.run_mode == RunMode.KUBERNETES:
            self.mlplatform_addr = os.environ["mlplatformAddr"]

            self.mlplatform_client = MlPlatformHttpClient(
                mlplatform_addr=self.mlplatform_addr, api_client=api_client
            )
            self.train_do_id = int(os.environ["doId"]) if "doId" in os.environ else None
            self.inference_do_id = int(os.environ["doId"]) if "doId" in os.environ else None
            self.train_data_object_info_list: List[ExperimentDataObjectInfo] = [from_dict(ExperimentDataObjectInfo, dict) for dict in os.environ["experimentDataObjectInfoList"]] if "experimentDataObjectInfoList" in os.environ else []
            self.mount_path = self.api_client.pvc_mount_path
            if "servingMountPath" in os.environ:
                # shutil.rmtree(os.environ["mount_path"])
                self.serving_mount_path = os.environ["servingMountPath"]
                Path(os.path.dirname(self.mount_path)).mkdir(parents=True, exist_ok=True)
                os.symlink(self.serving_mount_path, self.mount_path)
            else:
                Path(self.get_experiment_path()).mkdir(parents=True, exist_ok=True)
                Path(self.get_train_path()).mkdir(parents=True, exist_ok=True)
                if self.inference_id is not None:
                    Path(self.get_inference_path()).mkdir(parents=True, exist_ok=True)

    def download_train_csv(self) -> str:
        return self.hyperdata_api.download_csv(
            do_id=int(self.train_do_id), data_rootpath=self.get_experiment_path(),
        )

    def download_train_csv_from_data_key(self, key: str) -> str:
        do_id = None
        for data_object_info in self.train_data_object_info_list:
            if data_object_info.key == key:
                do_id = data_object_info.do_id
        return self.hyperdata_api.download_csv(
            do_id=do_id, data_rootpath=self.get_experiment_path()
        )

    def download_retrain_csv(self) -> str:
        return self.download_train_csv()

    def download_inference_csv(self) -> str:
        return self.hyperdata_api.download_csv(
            do_id=int(self.inference_do_id), data_rootpath=self.get_inference_path(),
        )

    def get_train_id(self) -> int:
        return self.train_id

    def get_inference_id(self) -> int:
        return self.inference_id

    def get_experiment_path(self) -> str:
        experiment_path = os.path.join(self.mount_path, f"experiment-{self.experiment_id}")
        if "servingMountPath" not in os.environ:
            Path(experiment_path).mkdir(parents=True, exist_ok=True)
        return experiment_path

    def get_train_path(self) -> str:
        train_path = os.path.join(self.get_experiment_path(), f"train-{self.train_id}")
        if "servingMountPath" not in os.environ:
            Path(train_path).mkdir(parents=True, exist_ok=True)
        return train_path

    def get_prev_train_path(self) -> List[str]:
        return [
            os.path.join(self.get_experiment_path(), str(train_id))
            for train_id in range(1, self.get_train_id())
        ]

    def get_inference_path(self):
        inference_path = os.path.join(self.get_experiment_path(), f"inference-{self.inference_id}")
        if "servingMountPath" not in os.environ:
            Path(inference_path).mkdir(parents=True, exist_ok=True)
        return inference_path

    def get_inference_csv_path(self):
        return os.path.join(self.get_inference_path(), "inference.csv")

    def insert_model_info(self, model_id: int, model_info: ModelInfoDto) -> ModelInfoDto:
        return self.mlplatform_client.insert_model_info(
            experiment_id=self.experiment_id, train_id=self.train_id, model_id=model_id, model_info=model_info
        )

    def upload_model(self, model_id: int, model_path: str):
        return self.mlplatform_client.upload_model(
            experiment_id=self.experiment_id, train_id=self.train_id, model_id=model_id, model_path=model_path
        )
