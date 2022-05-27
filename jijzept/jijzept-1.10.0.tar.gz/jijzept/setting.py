import pathlib

import toml


def load_config(file_name: str, config="default") -> dict:
    """Loads config file (TOML file).

    Args:
        file_name (str): Path to config file.
        config (str, optional): Loading enviroment name. Defaults to 'default'.

    Raises:
        TypeError: If 'config' enviroment is not defined in config file.

    Returns:
        dict: {'token': 'xxxx', 'url': 'xxxx'}
    """
    p_rel = pathlib.Path(file_name)
    with open(p_rel) as f:
        toml_setting_file = toml.load(f)
    if config not in toml_setting_file:
        raise TypeError(
            "'{}' is not defined in config file ({}).".format(config, file_name)
        )
    return toml_setting_file
