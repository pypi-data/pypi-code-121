
import json
import os
from typing import Union


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    data = None
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as json_file:
                data = json.load(json_file)
        except Exception:
            data = None
    if data is None:
        data = {}
    return data


def write_config(data: dict) -> None:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    json_object = json.dumps(data, indent=4)
    with open(config_path, 'w') as outfile:
        outfile.write(json_object)


def get_script_path() -> Union[str, None]:
    config = load_config()
    if 'script_path' in config:
        return config['script_path']

    return None


def save_script_path(script_path: str) -> None:
    config = load_config()
    config['script_path'] = script_path
    write_config(config)


def is_script_path_setted() -> bool:
    return 'script_path' in load_config()


trues = ['1', 'true', 'yes', 'on']


def get_config(key: str) -> bool:
    config = load_config()
    if key in config:
        send_errors: str = config[key]
        if len(send_errors) > 0:
            send_errors = send_errors.lower()
            return send_errors in trues
    return False
