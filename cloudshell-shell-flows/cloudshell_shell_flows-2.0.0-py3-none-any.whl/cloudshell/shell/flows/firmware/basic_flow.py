from __future__ import annotations

from abc import abstractmethod
from logging import Logger
from typing import TYPE_CHECKING

from cloudshell.logging.utils.decorators import command_logging

from cloudshell.shell.flows.interfaces import FirmwareFlowInterface
from cloudshell.shell.flows.utils.url import (
    BasicLocalUrl,
    ErrorParsingUrl,
    RemoteURL,
    ValidationError,
)

if TYPE_CHECKING:
    from cloudshell.shell.standards.core.resource_config_entities import (
        GenericResourceConfig,
    )


class AbstractFirmwareFlow(FirmwareFlowInterface):
    REMOTE_URL_CLASS = RemoteURL
    LOCAL_URL_CLASS = BasicLocalUrl

    def __init__(self, logger: Logger, resource_config: GenericResourceConfig):
        self._logger = logger
        self._timeout = 3600
        self._resource_config = resource_config

    @abstractmethod
    def _load_firmware_flow(
        self,
        firmware_url: REMOTE_URL_CLASS | LOCAL_URL_CLASS,
        vrf_management_name: str | None,
        timeout: int,
    ) -> None:
        raise NotImplementedError

    @command_logging
    def load_firmware(self, path: str, vrf_management_name: str | None = None) -> None:
        """Update firmware version on device by loading provided image.

        Performs following steps:

            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param path: full path to firmware file on ftp/tftp location
        :param vrf_management_name: VRF Name
        :return: status / exception
        """
        url = self._get_firmware_url(path)
        vrf_management_name = self._get_vrf_mgmt_name(vrf_management_name)
        self._load_firmware_flow(url, vrf_management_name, self._timeout)

    def _get_vrf_mgmt_name(self, vrf_name: str | None) -> str | None:
        return vrf_name or getattr(self._resource_config, "vrf_management_name", None)

    def _get_firmware_url(self, path: str) -> REMOTE_URL_CLASS | LOCAL_URL_CLASS:
        try:
            url = self.REMOTE_URL_CLASS.from_str(path)
        except ValidationError:
            try:
                url = self.LOCAL_URL_CLASS.from_str(path)
            except ValidationError:
                raise ErrorParsingUrl(path)
        url.validate_filename_is_present()
        return url
