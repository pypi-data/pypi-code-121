from __future__ import annotations

import attr
import pytest

from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow
from cloudshell.shell.flows.utils.url import ErrorParsingUrl, FileNameIsNotPresent


@attr.s(auto_attribs=True, slots=True, frozen=True)
class ResourceConfig:
    vrf_management_name: str = "vrf name"


@pytest.fixture()
def resource_config():
    return ResourceConfig()


@pytest.fixture()
def firmware_flow_do_nothing(logger, resource_config):
    class TestedFlow(AbstractFirmwareFlow):
        def _load_firmware_flow(
            self,
            firmware_url,
            vrf_management_name: str | None,
            timeout: int,
        ) -> None:
            return

    return TestedFlow(logger, resource_config)


def test_abstract_flow(logger, resource_config):
    class TestedFlow(AbstractFirmwareFlow):
        def _load_firmware_flow(
            self,
            firmware_url,
            vrf_management_name: str | None,
            timeout: int,
        ) -> None:
            super()._load_firmware_flow(firmware_url, vrf_management_name, timeout)

    flow = TestedFlow(logger, resource_config)
    with pytest.raises(NotImplementedError):
        flow._load_firmware_flow("", None, 100)


@pytest.mark.parametrize(
    ("path", "vrf", "expected_url_str", "expected_vrf"),
    (
        ("ftp://user@host/file", "mgmt", "ftp://user@host/file", "mgmt"),
        ("tftp://host/file", None, "tftp://host/file", "vrf name"),
        ("flash://file", None, "flash://file", "vrf name"),
    ),
)
def test_load_firmware(
    path, vrf, expected_url_str, expected_vrf, logger, resource_config
):
    class TestedFlow(AbstractFirmwareFlow):
        def _load_firmware_flow(
            self,
            firmware_url,
            vrf_management_name: str | None,
            timeout: int,
        ) -> None:
            assert str(firmware_url) == expected_url_str
            assert vrf_management_name == expected_vrf

    flow = TestedFlow(logger, resource_config)
    flow.load_firmware(path, vrf)


def test_path_without_file(firmware_flow_do_nothing):
    with pytest.raises(FileNameIsNotPresent):
        firmware_flow_do_nothing.load_firmware("ftp://host")


def test_wrong_file_path(firmware_flow_do_nothing):
    with pytest.raises(ErrorParsingUrl):
        firmware_flow_do_nothing.load_firmware("file")
