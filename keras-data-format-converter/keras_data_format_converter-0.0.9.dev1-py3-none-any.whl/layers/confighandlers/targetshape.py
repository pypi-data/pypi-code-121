from typing import Dict, Any


def handle_transpose_target_shape(target_data_format: str, config: Dict[str, Any]) -> Dict[str, Any]:
    target_shape = config["target_shape"]
    if target_data_format == "channels_first":
        new_target_shape = [target_shape[-1], *target_shape[0:-1]]
    else:  # data_format == "channels_last"
        new_target_shape = [*target_shape[1:], target_shape[0]]
    config["target_shape"] = new_target_shape
    return config
