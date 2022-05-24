from __future__ import annotations

import pytest

from cloudshell.shell.flows.interfaces import (
    ConfigurationFlowInterface,
    FirmwareFlowInterface,
)


def test_configuration_flow_interface():
    class TestedFlow(ConfigurationFlowInterface):
        def save(
            self,
            folder_path: str,
            configuration_type: str,
            vrf_management_name: str | None = None,
            return_full_path: bool = False,
        ) -> str:
            return super().save(folder_path, configuration_type, vrf_management_name)

        def restore(
            self,
            path: str,
            configuration_type: str,
            restore_method: str,
            vrf_management_name: str | None,
        ) -> None:
            return super().restore(
                path, configuration_type, restore_method, vrf_management_name
            )

        def orchestration_save(
            self, mode: str = "shallow", custom_params: str | None = None
        ) -> str:
            return super().orchestration_save(mode, custom_params)

    flow = TestedFlow()
    with pytest.raises(NotImplementedError):
        flow.save("", "", None)
    with pytest.raises(NotImplementedError):
        flow.restore("", "", "", None)
    with pytest.raises(NotImplementedError):
        flow.orchestration_save()


def test_firmware_flow_interface():
    class TestedFlow(FirmwareFlowInterface):
        def load_firmware(self, path: str, vrf_management_name: str | None) -> None:
            super().load_firmware(path, vrf_management_name)

    flow = TestedFlow()
    with pytest.raises(NotImplementedError):
        flow.load_firmware("", None)
