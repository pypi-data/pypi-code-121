from worker_bunch.astral_times.astral_times_config import ASTRAL_TIMES_JSONSCHEMA
from worker_bunch.service_logging import LOGGING_JSONSCHEMA
from worker_bunch.database.database_config import DATABASE_CONNECTIONS_JSONSCHEMA
from worker_bunch.mqtt.mqtt_config import MQTT_JSONSCHEMA
from worker_bunch.worker.worker_config import WORKER_INSTANCES_JSONSCHEMA


class ConfigException(Exception):
    pass


class ServiceConfKey:
    LOCALE = "locale"
    DATA_DIR = "data_directory"


SERVICE_JSONSCHEMA = {
    "type": "object",
    "properties": {
        ServiceConfKey.LOCALE: {
            "type": "string",
            "minLength": 1,
            "description": "",
        },
        ServiceConfKey.DATA_DIR: {
            "type": "string",
            "minLength": 1,
            "description": "Promoted to workers, so they store their data there. Make sure it's writable. "
                           "Relative paths refer to config file.",
        },
    },
    "additionalProperties": False,
    "required": [],
}


class MainConfKey:
    ASTRAL_TIMES = "astral_times"
    DATABASE_CONNECTIONS = "database_connections"
    LOGGING = "logging"
    MQTT_BROKER = "mqtt_broker"
    SERVICE = "service"
    WORKER_INSTANCES = "worker_instances"
    WORKER_SETTINGS = "worker_settings"
    YAML_TEMPLATES = "yaml_templates"


CONFIG_JSONSCHEMA = {
    "type": "object",
    "properties": {
        MainConfKey.ASTRAL_TIMES: ASTRAL_TIMES_JSONSCHEMA,
        MainConfKey.DATABASE_CONNECTIONS: DATABASE_CONNECTIONS_JSONSCHEMA,
        MainConfKey.LOGGING: LOGGING_JSONSCHEMA,
        MainConfKey.MQTT_BROKER: MQTT_JSONSCHEMA,
        MainConfKey.SERVICE: SERVICE_JSONSCHEMA,
        MainConfKey.WORKER_INSTANCES: WORKER_INSTANCES_JSONSCHEMA,
        MainConfKey.WORKER_SETTINGS: {
            "type": "object",
            "description": "dummy section, will be filled with worker schemes based on configuration."
        },
        MainConfKey.YAML_TEMPLATES: {
            "type": "object",
            "additionalProperties": True,
            "description": "The strict schema prevents putting objects anywhere outside of given structure. This constrains the YAML "
                           "reference feature. Therefor this section is supposed to contain arbitrary objects without a schema validation. "
                           "Also nothing within this section is used by worker-bunch directly. So put your reused YAML referenced objects "
                           "here."
        },
    },
    "additionalProperties": False,
    "required": [MainConfKey.WORKER_INSTANCES],
}
