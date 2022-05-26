from typing import Dict, Any


def handle_axis_change(target_data_format: str, config: Dict[str, Any]) -> Dict[str, Any]:
    transposed_axis = -1
    if target_data_format == "channels_first":
        transposed_axis = 1
    config["axis"] = transposed_axis
    return config
