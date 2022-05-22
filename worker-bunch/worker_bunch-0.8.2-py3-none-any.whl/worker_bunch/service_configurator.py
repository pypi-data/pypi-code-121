import copy
import locale
import logging
import os
import pathlib
import uuid
from typing import Dict, Optional

import yaml
from jsonschema import validate

from worker_bunch.service_config import MainConfKey, CONFIG_JSONSCHEMA, ServiceConfKey, ConfigException
from worker_bunch.worker.worker_config import WorkerSettingsDeclaration

_logger = logging.getLogger(__name__)


class ServiceConfigurator:

    def __init__(self):
        self._config_data = {}
        self._config_file: Optional[str] = None

    def read_config_file(self, config_file, skip_file_access_check=False):
        self._config_file = os.path.abspath(config_file)

        if not skip_file_access_check:
            self.check_config_file_access(self._config_file)

        with open(self._config_file, 'r') as stream:
            file_data = yaml.unsafe_load(stream)

        # first validation without worker config
        validate(file_data, CONFIG_JSONSCHEMA)

        self._config_data = file_data

        # ensure service section, which will be made available to workers
        service_settings = self._config_data.get(MainConfKey.SERVICE)
        if service_settings is None:
            service_settings = {}
            self._config_data[MainConfKey.SERVICE] = service_settings

    def init_locale(self):
        locale_name = self.get_service_config().get(ServiceConfKey.LOCALE)

        try:
            if locale_name:
                locale_was_set = locale.setlocale(locale.LC_ALL, locale_name.strip())
                _logger.debug("set locale: '%s'", locale_was_set)
        except locale.Error as ex:
            raise ConfigException(f"set locale failed (use e.g. 'de_DE.UTF8', not '{locale_name}'): {ex}")

    def init_data_dir(self):
        service_settings = self.get_service_config()
        data_dir = service_settings.get(ServiceConfKey.DATA_DIR)

        if not data_dir:
            _logger.info("no data dir configured. workers may not be able to write to disc.")
            return

        if not os.path.isabs(data_dir):
            dirname = os.path.dirname(self._config_file)
            data_dir = os.path.realpath(os.path.join(dirname, data_dir))
            service_settings[ServiceConfKey.DATA_DIR] = data_dir

        if not os.path.isdir(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
            except PermissionError as ex:
                raise ConfigException(f"Provide a proper, writable data directory! '{data_dir}': {ex}")

        # check write permission
        for i in range(1, 3):
            touch_file = os.path.join(data_dir, f"touch-test.{str(uuid.uuid4())}")
            if not os.path.exists(touch_file):
                try:
                    pathlib.Path(touch_file).touch()
                    os.remove(touch_file)
                    break
                except Exception as ex:
                    raise ConfigException(f"Data dir write check failed! {ex}")
        # ... _logger.info("could not check data dir write permission...?!")

    @classmethod
    def create_extended_json_schema(cls, declarations: Dict[str, WorkerSettingsDeclaration]) -> Dict[str, any]:
        schema = copy.deepcopy(CONFIG_JSONSCHEMA)

        worker_settings_schema = {"type": "object"}
        worker_settings_schema["additionalProperties"] = False

        settings_entries = {}
        worker_settings_schema["properties"] = settings_entries
        settings_required = []
        worker_settings_schema["required"] = settings_required

        for worker_name, extra_config in declarations.items():
            if extra_config.settings_schema:
                settings_entries[worker_name] = extra_config.settings_schema
                if extra_config.required:
                    settings_required.append(worker_name)

        schema["properties"][MainConfKey.WORKER_SETTINGS] = worker_settings_schema
        return schema

    def revalidate_worker_settings(self, declarations: Dict[str, WorkerSettingsDeclaration]):
        extended_schema = self.create_extended_json_schema(declarations)
        validate(self._config_data, extended_schema)

    def get_worker_instances_config(self):
        return self._config_data.get(MainConfKey.WORKER_INSTANCES, {})

    def get_worker_settings(self):
        return self._config_data.get(MainConfKey.WORKER_SETTINGS, {})

    def get_logging_config(self):
        return self._config_data.get(MainConfKey.LOGGING, {})

    def get_mqtt_config(self):
        return self._config_data.get(MainConfKey.MQTT_BROKER, {})

    def get_astral_config(self):
        return self._config_data.get(MainConfKey.ASTRAL_TIMES, {})

    def get_database_config(self):
        return self._config_data.get(MainConfKey.DATABASE_CONNECTIONS, {})

    def get_service_config(self):
        return self._config_data[MainConfKey.SERVICE]

    def get_data_dir(self) -> str:
        service_settings = self.get_service_config()
        return service_settings.get(ServiceConfKey.DATA_DIR)

    @classmethod
    def check_config_file_access(cls, config_file):
        if not os.path.isfile(config_file):
            raise FileNotFoundError('config file ({}) does not exist!'.format(config_file))

        permissions = oct(os.stat(config_file).st_mode & 0o777)[2:]
        if permissions != "600":
            extra = "change via 'chmod'. this config file may contain sensitive information."
            raise PermissionError(f"wrong config file permissions ({config_file}: expected 600, got {permissions})! {extra}")

    @classmethod
    def generate_config_file_json_schema(cls, workers_extra_configs: Optional[Dict[str, WorkerSettingsDeclaration]]):
        if workers_extra_configs:
            schema = cls.create_extended_json_schema(workers_extra_configs)
        else:
            schema = CONFIG_JSONSCHEMA
        return schema
