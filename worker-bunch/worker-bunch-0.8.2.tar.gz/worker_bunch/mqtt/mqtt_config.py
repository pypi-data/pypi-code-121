
class MqttConfKey:
    CLIENT_ID = "client_id"
    HOST = "host"
    PORT = "port"
    PASSWORD = "password"
    USER = "user"
    KEEPALIVE = "keepalive"
    PROTOCOL = "protocol"
    DEFAULT_QOS = "default_qos"
    DEFAULT_RETAIN = "default_retain"

    SSL_CA_CERTS = "ssl_ca_certs"
    SSL_CERTFILE = "ssl_certfile"
    SSL_INSECURE = "ssl_insecure"
    SSL_KEYFILE = "ssl_keyfile"


MQTT_JSONSCHEMA = {
    "type": "object",
    "properties": {
        MqttConfKey.CLIENT_ID: {"type": "string", "minLength": 1},
        MqttConfKey.DEFAULT_QOS: {"type": "integer", "enum": [0, 1, 2]},
        MqttConfKey.DEFAULT_RETAIN: {
            "type": "boolean",
            "description": "Default: True. May be overwritten in your worker."},
        MqttConfKey.HOST: {"type": "string", "minLength": 1},
        MqttConfKey.KEEPALIVE: {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum period in seconds between communications with the broker"
        },
        MqttConfKey.PASSWORD: {"type": "string"},
        MqttConfKey.PORT: {"type": "integer"},
        MqttConfKey.PROTOCOL: {"type": "integer", "enum": [3, 4, 5]},
        MqttConfKey.SSL_CA_CERTS: {"type": "string", "minLength": 1},
        MqttConfKey.SSL_CERTFILE: {"type": "string", "minLength": 1},
        MqttConfKey.SSL_INSECURE: {"type": "boolean"},
        MqttConfKey.SSL_KEYFILE: {"type": "string", "minLength": 1},
        MqttConfKey.USER: {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
    "required": [MqttConfKey.HOST],
}
