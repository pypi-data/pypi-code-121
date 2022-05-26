from mlplatform_lib.api_client import ApiClient, RunMode
from mlplatform_lib.mllab.mllab_http_client import MllabHttpClient
from mlplatform_lib.hyperdata.hyperdata_http_client import HyperdataHttpClient
from mlplatform_lib.hyperdata.hyperdata_api import HyperdataApi
from mlplatform_lib.virtualization.virtualization_api import VirtualizationApi
from mlplatform_lib.dataclass.model.model_dto import ModelDto
from mlplatform_lib.dataclass import (
    InsertTupleObject,
    TableColumnInfo,
)
import os
import pandas as pd
import sys
from typing import List, Optional, Union


class MllabImageType:
    TENSORFLOW_V1 = "tf_v1.15.2"
    TENSORFLOW_V2 = "tf_v2.1.0"
    TORCH = "torch_v1.6.0"


if "image" in os.environ:
    if (
        os.environ["image"] == MllabImageType.TENSORFLOW_V1
        or os.environ["image"] == MllabImageType.TENSORFLOW_V2
    ):
        import tensorflow as tf
    elif os.environ["image"] == MllabImageType.TORCH:
        import torch


class MllabApi:
    def __init__(self, api_client: ApiClient = None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        if api_client.run_mode == RunMode.KUBERNETES:
            self.mllab_mlplatform_client = MllabHttpClient(
                mlplatform_addr=os.environ["mlplatformAddr"], api_client=api_client
            )
            self.mllab_hyperdata_client = HyperdataHttpClient(
                hd_addr=self.api_client.hyperdata_addr, api_client=self.api_client
            )
            self.mllab_hyperdata_api = HyperdataApi(api_client=self.api_client)
            self.mllab_virtualization_api = VirtualizationApi(api_client=self.api_client)
        self.experiment_id = self.api_client.experiment_id
        self.image = os.environ["image"]

    def get_model_list(self) -> Optional[List[ModelDto]]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            return self.mllab_mlplatform_client.get_model_list(experiment_id=self.experiment_id)
        else:
            print("Current mode is local, Skip get_list_model.")
            return None

    def get_model(self):
        if self.api_client.run_mode == RunMode.KUBERNETES:
            
            model_path = self.api_client.pvc_mount_path + "/model/model-" + self.api_client.train_id + "/1"

            if self.image == MllabImageType.TENSORFLOW_V1:
                return tf.compat.v2.saved_model.load(model_path + "/")
            elif self.image == MllabImageType.TENSORFLOW_V2:
                return tf.saved_model.load(model_path + "/")
            elif self.image == MllabImageType.TORCH:
                sys.path.append(model_path + "/")
                return torch.jit.load(model_path + "/" + "model.pt")
        else:
            print("Current mode is local, Skip get_list_do.")
            return None

    def save_model(self, model, signatures=None) -> bool:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            export_dir = self.api_client.pvc_mount_path + "/model/model-" + self.api_client.train_id
            model_dir = export_dir + "/1"
            inference_dir = export_dir + "/inference"
            if not os.path.isdir(model_dir):
                os.makedirs(model_dir)
            if not os.path.isdir(inference_dir):
                os.makedirs(inference_dir)

            if self.image == MllabImageType.TENSORFLOW_V1:
                tf.saved_model.save(model, model_dir, signatures)
            elif self.image == MllabImageType.TENSORFLOW_V2:
                tf.saved_model.save(model, model_dir, signatures)
            elif self.image == MllabImageType.TORCH:
                jit_saved = torch.jit.script(model)
                jit_saved.save(model_dir + "/model.pt")

            model_dto = self.mllab_mlplatform_client.get_model_by_id(
                experiment_id=self.experiment_id, train_id=self.api_client.train_id
            )
            model_dto.model_path = model_dir
            self.mllab_mlplatform_client.update_model(
                experiment_id=self.experiment_id, train_id=self.api_client.train_id, dto=model_dto
            )
        else:
            print("Current mode is local, Skip get_list_do.")
            return None

    def get_do_list(self) -> dict:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            return self.mllab_hyperdata_client.get_do_simple_list()
        else:
            print("Current mode is local, Skip get_list_do.")
            return None

    def get_do(self, do_id: str, char_encoding="euc-kr") -> pd.DataFrame:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            file_name = do_id + ".csv"
            dir_name = self.api_client.pvc_mount_path + "/data"
            full_path = dir_name + "/" + file_name
            if os.path.exists(full_path):
                result = pd.read_csv(full_path, encoding=char_encoding)
                return result

            do_path = self.mllab_hyperdata_api.download_csv(do_id=do_id, data_rootpath=dir_name)

            if os.path.exists(do_path):
                result = pd.read_csv(do_path, encoding=char_encoding)
            else:
                print("Fail")
                result = None
            return result
        else:
            print("Current mode is local, Skip get_do.")
            return None

    def get_do_test(self, do_id: str) :
        print("Start get_do_test")
        self.mllab_virtualization_api.download_unstructured(do_id=do_id)

    def get_do_meta(self, do_id: str) -> List[TableColumnInfo]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            tableDescInfo = self.mllab_hyperdata_client.get_do_detail_info(do_id=do_id)
            return tableDescInfo.col_info_list
        else:
            print("Current mode is local, Skip get_do_meta.")
            return None

    def _get_inference_result_table_name(self, inference_id: int) -> str:
        mllab_experiment_dto = self.mllab_mlplatform_client.get_experiment(experiment_id=self.experiment_id)
        return f"MLLAB_{mllab_experiment_dto.name}_{str(mllab_experiment_dto.id)}"

    def save_inference_result(self, input_data: pd.DataFrame, do_id: Optional[str]= None, is_truncated: bool = True) -> bool:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            if self.api_client.inference_id is not None:
                file_dir = (
                    self.api_client.pvc_mount_path + "/model/model-" + self.api_client.train_id + "/inference/inference-" + self.api_client.inference_id
                )
                file_path = file_dir + "/inference-result.csv"
                if not os.path.isdir(file_dir):
                    os.mkdir(file_dir)
                input_data.to_csv(file_path, index=False, header=True)
            else:
                print("inference id is None")
                return False
        
            inference_dto = self.mllab_mlplatform_client.get_inference_by_id(
                experiment_id=self.experiment_id, train_id=self.api_client.train_id, model_id=self.api_client.model_id,inference_id=self.api_client.inference_id
            )
            inference_dto.inference_path = file_path
            self.mllab_mlplatform_client.update_inference( experiment_id=self.experiment_id, train_id=self.api_client.train_id, model_id=self.api_client.model_id, dto=inference_dto)

            if(do_id is None):
                 #create do in default source to save inference result
                table_name = self._get_inference_result_table_name(inference_dto.id)
                do_id = self.mllab_hyperdata_api.create_inference_result(
                    table_name=table_name, object_name=table_name, columns=input_data.columns.tolist()
                )

            insert_tuple_object = InsertTupleObject(
                isTruncated=is_truncated,
                targetColNames=input_data.columns.tolist(),
                tableData=input_data.values.tolist(),
            )
            res = self.mllab_hyperdata_client.insert_dataobject_tuple(
                dataobject_id=do_id, insert_tuple_objects=insert_tuple_object
            )
            if res.status_code == 200:
                return True
            else:
                return False
        else:
            print("Current mode is local, Skip save_inference_result.")

    

        
