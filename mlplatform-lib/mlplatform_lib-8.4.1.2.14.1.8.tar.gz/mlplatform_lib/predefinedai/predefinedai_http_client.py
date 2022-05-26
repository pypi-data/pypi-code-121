from mlplatform_lib.mlplatform.mlplatform_http_client import (
    MlPlatformHttpClient,
    MlPlatformRequestType,
)
from mlplatform_lib.dataclass.experiment import ExperimentPredefinedaiDto
from mlplatform_lib.dataclass.model import ModelPredefinedaiDto
from mlplatform_lib.dataclass.inference import InferencePredefinedaiDto
from typing import List
from mlplatform_lib.utils.dataclass_utils import to_dict, from_dict


class PredefinedAIHttpClient(MlPlatformHttpClient):
    def __init__(self, mlplatform_addr, api_client):
        super().__init__(mlplatform_addr=mlplatform_addr, api_client=api_client)

    def get_models(self, experiment_id: int, train_id: int) -> List[ModelPredefinedaiDto]:
        res = self.send_request(
            "models", {"experiments": experiment_id, "trains": train_id}, {}, {}, MlPlatformRequestType.READ,
        )
        model_infos = []
        for model_info in res.data:
            model_infos.append(from_dict(ModelPredefinedaiDto, model_info))
        return model_infos

    def insert_model(
        self, experiment_id: int, train_id: int, model: ModelPredefinedaiDto
    ) -> ModelPredefinedaiDto:
        res = self.send_request(
            "models",
            {"experiments": experiment_id, "trains": train_id},
            {},
            to_dict(model),
            MlPlatformRequestType.CREATE,
        )
        return from_dict(ModelPredefinedaiDto, res.data)

    def get_experiment(self, experiment_id: int) -> ExperimentPredefinedaiDto:
        result = self.send_request("", {"experiments": experiment_id}, {}, {}, MlPlatformRequestType.READ)
        return from_dict(ExperimentPredefinedaiDto, result.data)

    def get_inference(self, experiment_id: int, inference_id: int) -> InferencePredefinedaiDto:
        result = self.send_request(
            "",
            {"experiments": experiment_id, "inferences": inference_id},
            {},
            {},
            MlPlatformRequestType.READ,
        )
        return from_dict(InferencePredefinedaiDto, result.data)

    def update_inference(
        self, experiment_id: int, inference_predefinedai_dto: InferencePredefinedaiDto
    ) -> InferencePredefinedaiDto:
        result = self.send_request(
            "inferences",
            {"experiments": experiment_id},
            {},
            to_dict(inference_predefinedai_dto),
            MlPlatformRequestType.UPDATE,
        )
        return from_dict(InferencePredefinedaiDto, result.data)
