from typing import Dict, Any


def handle_transpose_dims(target_data_format: str, config: Dict[str, Any]) -> Dict[str, Any]:
    dims = config["dims"]
    if target_data_format == "channels_first":
        channels_dim = len(dims)
        new_channels_dim = 1
        new_dims = []
        for dim in dims:
            if dim == channels_dim:
                new_dims.append(new_channels_dim)
            else:
                new_dims.append(dim + 1)

        ch_dim = new_dims.pop()
        new_dims.insert(0, ch_dim)
    else:
        channels_dim = 1
        new_channels_dim = len(dims)
        new_dims = []
        for dim in dims:
            if dim == channels_dim:
                new_dims.append(new_channels_dim)
            else:
                new_dims.append(dim - 1)

        ch_dim = new_dims.pop(0)
        new_dims.append(ch_dim)

    config["dims"] = new_dims
    return config
