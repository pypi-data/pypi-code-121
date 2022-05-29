from pathlib import Path


LOCAL_CONFIG_PATH = Path.home() / Path('.config/hurocon/config.json')
LOCAL_CONFIG_DEFAULT = {
    "config_version": 2,
    "connection_address": "http://192.168.8.1/",
    "auth": {
        "username": "admin",
        "password": "YWRtaW4="
    }
}
