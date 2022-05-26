from mlplatform_lib.mlplatform.mlplatform_http_client import (
    MlPlatformHttpClient,
    MlPlatformRequestType,
)
from mlplatform_lib.dataclass.experiment import ExperimentMllabDto
from mlplatform_lib.dataclass.model.model_dto import ModelDto
from mlplatform_lib.dataclass.inference.inference_dto import InferenceDto
from mlplatform_lib.utils.dataclass_utils import from_dict, to_dict
from typing import List


class MllabHttpClient(MlPlatformHttpClient):
    def __init__(self, mlplatform_addr, api_client):
        super().__init__(mlplatform_addr=mlplatform_addr, api_client=api_client)

    def get_experiment(self, experiment_id: int) -> ExperimentMllabDto:
        result = self.send_request("", {"experiments": experiment_id}, {}, {}, MlPlatformRequestType.READ)
        return from_dict(ExperimentMllabDto, result.data)

    def get_model_list(self, experiment_id: int) -> List[ModelDto]:
        res = self.send_request(
            "models", {"experiments": experiment_id}, {}, {}, MlPlatformRequestType.READ
        )

        model_infos = []
        for model_info in res.data:
            model_infos.append(from_dict(ModelDto, model_info))
        return model_infos

    def get_model_by_id(self, experiment_id: int, train_id: int) -> ModelDto:
        res = self.send_request(
            "models",
            {"experiments": experiment_id, "trains": train_id},
            {},
            {},
            MlPlatformRequestType.READ,
        )

        model_infos = []
        for model_info in res.data:
            model_infos.append(from_dict(ModelDto, model_info))
        return model_infos[0]

    def update_model(
        self, experiment_id: int, train_id: int, dto: ModelDto
    ) -> dict:
        res = self.send_request(
            "models",
            {"experiments": experiment_id, "trains": train_id},
            {},
            to_dict(dto),
            MlPlatformRequestType.UPDATE,
        )
        if res.status_code == 200:
            return True
        else:
            return False

    def get_latest_model(self, experiment_id=int) -> ModelDto:
        res = self.send_request(
            "models",
            {"experiments": experiment_id},
            {"latest": "latest"},
            {},
            MlPlatformRequestType.READ,
        )
        return from_dict(ModelDto, res.data[0])

    def get_inference_by_id(
        self, experiment_id: int, inference_id: int
    ) -> InferenceDto:
        res = self.send_request(
            "",
            {"experiments": experiment_id, "inferences": inference_id},
            {},
            {},
            MlPlatformRequestType.READ,
        )

        return from_dict(InferenceDto, res.data)

    def update_inference(self, experiment_id: int, dto: InferenceDto) -> dict:
        res = self.send_request(
            "inferences",
            {"experiments": experiment_id},
            {},
            to_dict(dto),
            MlPlatformRequestType.UPDATE,
        )
        if res.status_code == 200:
            return True
        else:
            return False
