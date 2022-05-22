

class DatabaseConfKey:

    # database connection
    HOST = "host"
    USER = "user"
    PORT = "port"
    PASSWORD = "password"
    DATABASE = "database"
    TIMEZONE = "timezone"
    AUTO_COMMIT = "auto_commit"

    # database worker
    CONNECTION_KEY = "connection_key"
    CRON = "cron"
    STEPS = "steps"

    # database step
    MQTT_LAST_WILL = "mqtt_last_will"
    MQTT_OUTPUT_TYPE = "mqtt_output_type"
    MQTT_RETAIN = "mqtt_retain"
    MQTT_TOPIC = "mqtt_topic"
    REPLACEMENTS = "replacements"
    SCRIPT_FILE = "script_file"
    STATEMENT = "statement"


DATABASE_CONNECTION_JSONSCHEMA = {
    "additionalProperties": False,
    "required": [DatabaseConfKey.HOST, DatabaseConfKey.PORT, DatabaseConfKey.DATABASE],
    "type": "object",
    "properties": {
        DatabaseConfKey.HOST: {"type": "string", "minLength": 1, "description": "Database host"},
        DatabaseConfKey.PORT: {"type": "integer", "minimum": 1, "description": "Database port"},
        DatabaseConfKey.USER: {"type": "string", "minLength": 1, "description": "Database user"},
        DatabaseConfKey.PASSWORD: {"type": "string", "minLength": 1, "description": "Database password"},
        DatabaseConfKey.DATABASE: {"type": "string", "minLength": 1, "description": "Database name"},
        DatabaseConfKey.TIMEZONE: {"type": "string", "minLength": 1, "description": "Predefined session timezone"},
        DatabaseConfKey.AUTO_COMMIT: {"type": "boolean"},
    },
}


DATABASE_CONNECTIONS_JSONSCHEMA = {
    "type": "object",
    "additionalProperties": DATABASE_CONNECTION_JSONSCHEMA,
    "description": "Dictionary of <database-connection-name>:<database-connection-properties>"
}


class MqttOutputType:
    JSON = "json"
    NONE = "none"
    SCALAR = "scalar"


MQTT_OUTPUT_TYPES = [MqttOutputType.JSON, MqttOutputType.NONE, MqttOutputType.SCALAR]


DATABASE_STEP_JSONSCHEMA = {
    "additionalProperties": False,
    "oneOf": [{"required": [DatabaseConfKey.STATEMENT]}, {"required": [DatabaseConfKey.SCRIPT_FILE]}],
    "type": "object",
    "properties": {
        DatabaseConfKey.MQTT_LAST_WILL: {"type": "string", "minLength": 1, "description": "MQTT last will"},
        DatabaseConfKey.MQTT_OUTPUT_TYPE: {
            "type": "string",
            "enum": MQTT_OUTPUT_TYPES,
            "description": "'scalar': publishes a single stringified value; 'json': publishes JSON (first row); 'none': publishes nothing",
        },
        DatabaseConfKey.MQTT_RETAIN: {"type": "boolean"},
        DatabaseConfKey.MQTT_TOPIC: {"type": "string", "minLength": 1, "description": "MQTT target topic"},
        DatabaseConfKey.SCRIPT_FILE: {"type": "string", "minLength": 1, "description": "SQL script file (statement has priority)"},
        DatabaseConfKey.STATEMENT: {"type": "string", "minLength": 1, "description": "SQL statement"},
        DatabaseConfKey.REPLACEMENTS: {
            "additionalProperties": {"type": "string"},
            "description": "Key/value pairs: replace all occurrences of the key with the value within statement.",
            "type": "object",
        },
    },
}


DATABASE_WORKER_JSONSCHEMA = {
    "additionalProperties": False,
    "required": [DatabaseConfKey.CONNECTION_KEY, DatabaseConfKey.CRON, DatabaseConfKey.STEPS],
    "type": "object",
    "properties": {
        DatabaseConfKey.CONNECTION_KEY: {"type": "string", "minLength": 1, "description": "Database connection key"},
        # TODO https://stackoverflow.com/questions/14203122/create-a-regular-expression-for-cron-statement
        DatabaseConfKey.CRON: {"type": "string", "minLength": 9, "description": "CRON syntax"},
        DatabaseConfKey.REPLACEMENTS: {
            "additionalProperties": {"type": "string"},
            "description": "Key/value pairs: Worker wide configuration. May be overwritten by steps. "
                           "Replace all occurrences of the key with the value within statements.",
            "type": "object",
        },
        DatabaseConfKey.STEPS: {
            "type": "array",
            "items": DATABASE_STEP_JSONSCHEMA,
            "description": "List of MQTT topics to read from",
            "minItems": 1,
        }
    },
}
