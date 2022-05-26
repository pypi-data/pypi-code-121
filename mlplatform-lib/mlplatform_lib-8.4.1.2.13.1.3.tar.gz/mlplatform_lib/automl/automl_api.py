import os
from typing import List, Optional

import pandas as pd

from mlplatform_lib.api_client import ApiClient, RunMode
from mlplatform_lib.automl.automl_http_client import AutomlHttpClient
from mlplatform_lib.dataclass import InsertTupleObject
from mlplatform_lib.dataclass.experiment.type import ExperimentType
from mlplatform_lib.dataclass.model import ModelInfoDto, ModelAutomlDto, ModelAutomlBestDto
from mlplatform_lib.dataclass.model.type import ModelStatus
from mlplatform_lib.hyperdata import HyperdataApi


class AutomlApi:
    def __init__(self, api_client: ApiClient = None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        if api_client.run_mode == RunMode.KUBERNETES:
            self.automl_client = AutomlHttpClient(
                mlplatform_addr=os.environ["mlplatformAddr"], api_client=self.api_client
            )
            self.hyperdata_api = HyperdataApi(api_client=self.api_client)
        self.experiment_id = self.api_client.experiment_id
        self.train_id = self.api_client.train_id
        self.inference_id = self.api_client.inference_id
        # self.target_do_id = os.environ["targetDoId"] if "targetDoId" in os.environ else None

    def get_models(self) -> Optional[List[ModelAutomlDto]]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            return self.automl_client.get_models(experiment_id=self.experiment_id, train_id=self.train_id,)
        else:
            print("Current mode is local, Skip get_models.")
            return None

    def insert_model(self, model: ModelAutomlDto) -> Optional[ModelAutomlDto]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            model.train_id = self.train_id
            model.status = ModelStatus.SUCCESS
            model.experiment_type = ExperimentType.AUTOML
            return self.automl_client.insert_model(
                experiment_id=self.experiment_id, train_id=self.train_id, model=model,
            )
        else:
            print("Current mode is local, Skip insert_model.")
            model.id = 1
            model.train_id = self.train_id
            model.status = ModelStatus.SUCCESS
            model.experiment_type = ExperimentType.AUTOML
            return model

    def insert_model_info(self, model_id: int, model_info: ModelInfoDto) -> ModelInfoDto:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            model_info.status = ModelStatus.SUCCESS
            return self.automl_client.insert_model_info(
                experiment_id=self.experiment_id,
                train_id=self.train_id,
                model_id=model_id,
                model_info=model_info,
            )
        else:
            print("Current mode is local, Skip insert_visualizations.")

    def _get_inference_result_table_name(self) -> str:
        automl_experiment_dto = self.automl_client.get_experiment(experiment_id=self.experiment_id)

        return f"AUTOML_{automl_experiment_dto.name}_{str(automl_experiment_dto.id)}"

    def upload_inference_csv(self, inference_csv_path: str):
        if self.api_client.run_mode == RunMode.KUBERNETES:
            inference_data = pd.read_csv(inference_csv_path)

            table_name = self._get_inference_result_table_name()
            self.target_do_id = self.hyperdata_api.create_inference_result(
                table_name=table_name, object_name=table_name, columns=inference_data.columns.tolist()
            )

            insert_tuple_object = InsertTupleObject(
                isTruncated="True",
                targetColNames=inference_data.columns.tolist(),
                tableData=inference_data.values.tolist(),
            )

            self.hyperdata_api.hyperdata_client.insert_dataobject_tuple(
                dataobject_id=self.target_do_id, insert_tuple_objects=insert_tuple_object,
            )

            automl_inference_dto = self.automl_client.get_inference(
                experiment_id=self.experiment_id, inference_id=self.inference_id
            )

            automl_inference_dto.target_do_id = self.target_do_id
            self.automl_client.update_inference(
                experiment_id=self.experiment_id, inference_automl_dto=automl_inference_dto,
            )
            os.remove(inference_csv_path)
        else:
            print("Current mode is local, Skip upload_inference_csv.")

    def insert_model_automl_best(self, model_automl_best: ModelAutomlBestDto) -> ModelAutomlBestDto:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            return self.automl_client.insert_model_automl_best(
                experiment_id=self.experiment_id, train_id=self.train_id, model_automl_best=model_automl_best,
            )
        else:
            print("Current mode is local, Skip insert_model_automl_best.")
