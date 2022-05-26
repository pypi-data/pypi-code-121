from typing import Any, Dict


def handle_data_format(target_data_format: str, config: Dict[str, Any]) -> Dict[str, Any]:
    if "data_format" in config:
        config["data_format"] = target_data_format
    return config

