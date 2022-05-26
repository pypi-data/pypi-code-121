import os
from enum import Enum
import yaml
from mlplatform_lib.utils.dataclass_utils import from_dict
from mlplatform_lib.dataclass.experiment import ExperimentDataObjectInfo


class RunMode(Enum):
    LOCAL = "local"
    KUBERNETES = "kubernetes"


class MlPlatformException(Exception):
    pass


class ApiClient:
    def __init__(self, server_config_path: str = None):
        # server_config_path가 none이면 pod에서 수행된다고 간주
        # 공용으로 사용하는 env 및 secret을 로드한다.
        if server_config_path is None or not os.path.isfile(server_config_path):
            print("Cannot found server_config_path. run kubernetes mode.")
            self.load_env()
            self.run_mode = RunMode.KUBERNETES
        else:
            self.load_server_config(server_config_path=server_config_path)
            self.server_config_path = server_config_path
            self.run_mode = RunMode.LOCAL

    def load_env(self):
        self.hyperdata_addr = os.environ["hyperdataAddr"]
        self.virtualization_addr = os.environ["virtualizationAddr"]
        self.proauth_addr = os.environ["proauthAddr"]
        self.experiment_id = os.environ["experimentId"]
        self.train_id = os.environ["trainId"] if "trainId" in os.environ else None
        self.model_id = os.environ["modelId"] if "modelId" in os.environ else None
        self.inference_id = os.environ["inferenceId"] if "inferenceId" in os.environ else None
        self.serving_id = os.environ["servingId"] if "servingId" in os.environ else None
        self.pvc_mount_path = os.environ["pvcMountPath"]
        self.serving_mount_path = os.environ["servingMountPath"] if "servingMountPath" in os.environ else None
        self.secret_mount_path = os.environ["secretMountPath"]
        file_list = [f for f in os.listdir(self.secret_mount_path)]

    def load_server_config(self, server_config_path):
        server_config = yaml.safe_load(open(server_config_path, "r"))
        try:
            self.hyperdata_addr = server_config["hyperdataAddr"]
            self.proauth_addr = server_config["proauthAddr"]
            self.user_id = server_config["userId"]
            self.user_password = server_config["userPassword"]
            self.project_name = server_config["projectName"]
            self.experiment_id = server_config["experimentId"]
            self.train_id = server_config["trainId"]
            self.model_id = server_config["modelId"]
            self.inference_id = server_config["inferenceId"]
            self.serving_id = server_config["servingId"]
            self.train_do_name = server_config["trainDoName"]
            self.inference_do_name = server_config["inferenceDoName"]
            self.train_data_object_info_list = [
                from_dict(ExperimentDataObjectInfo, dict) for dict in server_config["trainDataObjectInfoList"]] if "trainDataObjectInfoList" in server_config else []
        except KeyError as e:
            print(f'Cannot found "{str(e)}" in server_config.yaml')
            exit(1)
