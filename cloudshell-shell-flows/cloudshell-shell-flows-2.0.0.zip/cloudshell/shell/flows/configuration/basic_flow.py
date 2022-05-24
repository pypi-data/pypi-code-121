from __future__ import annotations

import re
import time
from abc import abstractmethod
from enum import Enum
from logging import Logger
from typing import TYPE_CHECKING

import jsonpickle

from cloudshell.logging.utils.decorators import command_logging

from cloudshell.shell.flows.interfaces import ConfigurationFlowInterface
from cloudshell.shell.flows.utils.errors import ShellFlowsException
from cloudshell.shell.flows.utils.url import (
    BasicLocalUrl,
    ErrorParsingUrl,
    RemoteURL,
    ValidationError,
)

if TYPE_CHECKING:
    from cloudshell.shell.standards.resource_config_generic_models import (
        GenericBackupConfig,
    )


class ConfigurationType(Enum):
    RUNNING = "running"
    STARTUP = "startup"

    @classmethod
    def from_str(cls, name: str) -> ConfigurationType:
        # raised ValueError for invalid configuration type
        return cls(name.lower())


class RestoreMethod(Enum):
    OVERRIDE = "override"
    APPEND = "append"

    @classmethod
    def from_str(cls, name: str) -> RestoreMethod:
        # raised ValueError for invalid restore method
        return cls(name.lower())


class ConfigurationTypeNotSupported(ShellFlowsException):
    def __init__(self, type_: ConfigurationType):
        self.configuration_type = type_
        super().__init__(f"Shell doesn't support '{type_.value}' configuration type")


class RestoreMethodNotSupported(ShellFlowsException):
    def __init__(self, method: RestoreMethod):
        self.restore_method = method
        super().__init__(f"Shell doesn't support '{method.value}' restore method")


class AbstractConfigurationFlow(ConfigurationFlowInterface):
    FILE_SYSTEM_SCHEME = "File System"
    MAX_CONFIG_FILE_NAME_LENGTH = 46  # prefix length is 23 symbols
    REMOTE_URL_CLASS = RemoteURL
    LOCAL_URL_CLASS = BasicLocalUrl
    SUPPORTED_CONFIGURATION_TYPES: set[ConfigurationType] = {
        ConfigurationType.RUNNING,
        ConfigurationType.STARTUP,
    }
    SUPPORTED_RESTORE_METHODS: set[RestoreMethod] = {
        RestoreMethod.OVERRIDE,
        RestoreMethod.APPEND,
    }

    def __init__(self, logger: Logger, resource_config: GenericBackupConfig):
        self._logger = logger
        self._resource_config = resource_config

    @property
    @abstractmethod
    def file_system(self) -> str:
        """Default File System scheme."""
        raise NotImplementedError

    @command_logging
    def save(
        self,
        folder_path: str,
        configuration_type: str,
        vrf_management_name: str | None = None,
        return_full_path: bool = False,
    ) -> str:
        """Backup config from the device to provided file system.

        :param folder_path: tftp/ftp server where file be saved
        :param configuration_type: type of configuration that will be saved
            (StartUp or Running)
        :param vrf_management_name: Virtual Routing and Forwarding management name
        :param return_full_path: return full path to saved config file which can
            include username and password
        :return: file name or full path to the file (can include username and password)
        """
        configuration_type = ConfigurationType.from_str(configuration_type)
        self._validate_configuration_type(configuration_type)
        vrf_management_name = self._get_vrf_mgmt_name(vrf_management_name)

        if folder_path:
            url = self._get_folder_url(folder_path)
        else:
            url = self._generate_folder_url_from_resource_config()
        self._add_auth(url)
        file_name = self._generate_config_file_name(configuration_type)
        url.add_filename(file_name)

        new_file_name = self._save_flow(url, configuration_type, vrf_management_name)
        if new_file_name:
            url.replace_filename(new_file_name)

        if return_full_path:
            file_path = str(url)
        else:
            file_path = url.filename
        return file_path

    @command_logging
    def orchestration_save(
        self, mode: str = "shallow", custom_params: str | None = None
    ) -> str:
        """Orchestration Save command.

        :param mode: is not used by current implementation
        :param custom_params: json with custom params
        :return: path to the saved config file
        """
        save_params = {
            "folder_path": "",
            "configuration_type": "running",
            "return_full_path": True,
        }
        params = {}
        if custom_params:
            params = jsonpickle.decode(custom_params)

        save_params.update(params.get("custom_params", {}))
        path = self.save(**save_params)

        return path

    @command_logging
    def restore(
        self,
        path: str,
        configuration_type: str,
        restore_method: str,
        vrf_management_name: str | None = None,
    ) -> None:
        """Restore configuration on device from provided configuration file.

        Restore configuration from local file system or ftp/tftp server into
        'running-config' or 'startup-config'.
        :param path: path to the file on the remote host, tftp://server/sourcefile
        :param configuration_type: the configuration type to restore
            (StartUp or Running)
        :param restore_method: override current config or not
        :param vrf_management_name: Virtual Routing and Forwarding management name
        """
        configuration_type = ConfigurationType.from_str(configuration_type)
        self._validate_configuration_type(configuration_type)
        vrf_management_name = self._get_vrf_mgmt_name(vrf_management_name)
        restore_method = RestoreMethod.from_str(restore_method)
        self._validate_restore_method(restore_method)

        url = self._get_config_url(path)
        self._add_auth(url)
        self._restore_flow(url, configuration_type, restore_method, vrf_management_name)

    def _validate_configuration_type(self, type_: ConfigurationType):
        if type_ not in self.SUPPORTED_CONFIGURATION_TYPES:
            raise ConfigurationTypeNotSupported(type_)

    def _validate_restore_method(self, method: RestoreMethod):
        if method not in self.SUPPORTED_RESTORE_METHODS:
            raise RestoreMethodNotSupported(method)

    @abstractmethod
    def _save_flow(
        self,
        file_dst_url: REMOTE_URL_CLASS | LOCAL_URL_CLASS,
        configuration_type: ConfigurationType,
        vrf_management_name: str | None,
    ) -> str | None:
        """Save flow, has to be implemented.

        :return: returns filename if changed it
        """
        raise NotImplementedError

    @abstractmethod
    def _restore_flow(
        self,
        config_path: REMOTE_URL_CLASS | LOCAL_URL_CLASS,
        configuration_type: ConfigurationType,
        restore_method: RestoreMethod,
        vrf_management_name: str | None,
    ) -> None:
        """Restore flow, has to be implemented."""
        raise NotImplementedError

    def _get_folder_url(self, path: str) -> REMOTE_URL_CLASS | LOCAL_URL_CLASS:
        try:
            url = self.REMOTE_URL_CLASS.from_str(path)
        except ValidationError:
            try:
                url = self.LOCAL_URL_CLASS.from_str(path)
            except ValidationError:
                raise ErrorParsingUrl(path)
        return url

    def _get_config_url(self, config_path: str) -> REMOTE_URL_CLASS | LOCAL_URL_CLASS:
        try:
            url = self.REMOTE_URL_CLASS.from_str(config_path)
        except ValidationError:
            try:
                url = self.LOCAL_URL_CLASS.from_str(config_path)
            except ValidationError:
                # if config_path is a file name we can get the URL with a default system
                try:
                    url = self.LOCAL_URL_CLASS.from_str(config_path, self.file_system)
                except ValidationError:
                    raise ErrorParsingUrl(config_path)
        url.validate_filename_is_present()
        return url

    def _generate_folder_url_from_resource_config(
        self,
    ) -> REMOTE_URL_CLASS | LOCAL_URL_CLASS:
        backup_location = self._resource_config.backup_location
        try:
            # backup location can contain full URL with the scheme
            url = self.REMOTE_URL_CLASS.from_str(backup_location)
        except ValidationError:
            # or without scheme 🤷
            scheme = self._resource_config.backup_type
            if not scheme or scheme.lower() == self.FILE_SYSTEM_SCHEME.lower():
                scheme = self.file_system
                url = self.LOCAL_URL_CLASS.from_str(backup_location, scheme)
            else:
                url = self.REMOTE_URL_CLASS.from_str(backup_location, scheme)
        return url

    def _add_auth(self, url: REMOTE_URL_CLASS | LOCAL_URL_CLASS) -> None:
        if url.support_auth():
            if not url.username:
                url.username = self._resource_config.backup_user
            if not url.password:
                url.password = self._resource_config.backup_password

    def _get_vrf_mgmt_name(self, vrf_name: str | None) -> str | None:
        return vrf_name or getattr(self._resource_config, "vrf_management_name", None)

    def _generate_config_file_name(self, configuration_type: ConfigurationType) -> str:
        """Generate config file name.

        <resource-name>-<configuration-type>-<date-time>
        Note: resource name can be truncated
        e.g. cisco-running-030522-125534
        """
        time_stamp = time.strftime("%d%m%y-%H%M%S", time.localtime())
        prefix = f"-{configuration_type.value}-{time_stamp}"
        assert len(prefix) < self.MAX_CONFIG_FILE_NAME_LENGTH
        resource_name_limit = self.MAX_CONFIG_FILE_NAME_LENGTH - len(prefix)

        system_name = re.sub(r"\s+", "_", self._resource_config.name)
        dst_filename = f"{system_name[:resource_name_limit]}{prefix}"
        return dst_filename
