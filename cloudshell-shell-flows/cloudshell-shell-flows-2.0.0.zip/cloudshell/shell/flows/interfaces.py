from __future__ import annotations

from abc import ABC, abstractmethod


class AutoloadFlowInterface(ABC):
    @abstractmethod
    def discover(self, supported_os, resource_model):
        pass


class ConfigurationFlowInterface(ABC):
    @abstractmethod
    def save(
        self,
        folder_path: str,
        configuration_type: str,
        vrf_management_name: str | None = None,
        return_full_path: bool = False,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def restore(
        self,
        path: str,
        configuration_type: str,
        restore_method: str,
        vrf_management_name: str | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def orchestration_save(
        self, mode: str = "shallow", custom_params: str | None = None
    ) -> str:
        raise NotImplementedError


class FirmwareFlowInterface(ABC):
    @abstractmethod
    def load_firmware(self, path: str, vrf_management_name: str | None) -> None:
        raise NotImplementedError


class RunCommandFlowInterface(ABC):
    @abstractmethod
    def run_custom_command(self, command):
        pass

    @abstractmethod
    def run_custom_config_command(self, command):
        pass


class StateFlowInterface(ABC):
    @abstractmethod
    def health_check(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass
