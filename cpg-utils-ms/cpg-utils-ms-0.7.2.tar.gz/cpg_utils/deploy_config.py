import json
import logging
from os import getenv
from typing import Any, Dict, Optional
from .secrets import SecretManager

deploy_config: "DeployConfig" = None
DEFAULT_CONFIG = {
    "cloud": "gcp",
    "sample_metadata_project": "sample-metadata",
    "sample_metadata_host": "http://localhost:8000",
    "analysis_runner_project": "analysis-runner",
    "analysis_runner_host": "http://localhost:8001",
}


class DeployConfig:

    _server_config: Dict[str, Any] = None
    _secret_manager: SecretManager = None

    @staticmethod
    def from_dict(config: Dict[str, str]) -> "DeployConfig":
        return DeployConfig(**config)

    @staticmethod
    def from_environment() -> "DeployConfig":
        deploy_config = json.loads(getenv("CPG_DEPLOY_CONFIG", json.dumps(DEFAULT_CONFIG)))
        # Allow individual field overrides.
        deploy_config["cloud"] = getenv("CLOUD", deploy_config["cloud"])
        deploy_config["sample_metadata_host"] = getenv("SM_HOST_URL", deploy_config["sample_metadata_host"])
        return DeployConfig.from_dict(deploy_config)

    def __init__(
        self,
        cloud: Optional[str],
        sample_metadata_project: Optional[str],
        sample_metadata_host: Optional[str],
        analysis_runner_project: Optional[str],
        analysis_runner_host: Optional[str],
    ):
        self.cloud = cloud or DEFAULT_CONFIG["cloud"]
        self.sample_metadata_project = sample_metadata_project or DEFAULT_CONFIG["sample_metadata_project"]
        self.sample_metadata_host = sample_metadata_host or DEFAULT_CONFIG["sample_metadata_host"]
        self.analysis_runner_project = analysis_runner_project or DEFAULT_CONFIG["analysis_runner_project"]
        self.analysis_runner_host = analysis_runner_host or DEFAULT_CONFIG["analysis_runner_host"]
        assert self.cloud in ("gcp", "azure"), f"Invalid cloud specification '{self.cloud}'"

    def to_dict(self) -> Dict[str, str]:
        return self.__dict__.copy()

    @property
    def secret_manager(self) -> SecretManager:
        if self._secret_manager is None:
            self._secret_manager = SecretManager.get_secret_manager(self.cloud)
        return self._secret_manager

    @property
    def server_config(self) -> Dict[str, Any]:
        if self._server_config is None:
            config = self.read_global_config("server-config")
            logging.info(f"setting deploy_config: {config}")
            self._server_config = json.loads(config)
        return self._server_config

    def read_project_id_config(self, project_id: str, config_key: str) -> str:
        config_host = project_id + "vault" if self.cloud == "azure" else project_id
        return self.secret_manager.read_secret(config_host, config_key)

    def read_global_config(self, config_key: str) -> str:
        return self.read_project_id_config(self.analysis_runner_project, config_key)

    def read_dataset_config(self, dataset: str, config_key: str) -> str:
        if dataset not in self.server_config:
            return ""
        dataset_id = self.server_config[dataset]["projectId"]
        return self.read_project_id_config(dataset_id, config_key)


def get_deploy_config() -> DeployConfig:
    global deploy_config
    if deploy_config is None:
        set_deploy_config_from_env()
    return deploy_config


def set_deploy_config(config: DeployConfig) -> None:
    global deploy_config
    logging.info(f"setting deploy_config: {json.dumps(config.to_dict())}")
    deploy_config = config


def set_deploy_config_from_env() -> None:
    set_deploy_config(DeployConfig.from_environment())


def get_server_config() -> Dict[str, Any]:
    return get_deploy_config().server_config
