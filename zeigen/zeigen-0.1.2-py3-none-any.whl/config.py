"""Configuration file handling."""
import errno
import os
import pkgutil
from pathlib import Path
from typing import Any
from typing import Union

import typer
from dynaconf import Dynaconf  # type: ignore
from dynaconf import Validator  # type: ignore
from loguru import logger

CONFIG_FILE_FORMAT = "toml"

VALIDATORS = [Validator("query", must_exist=True)]


def get_config_file_name(pkg_name: str) -> str:
    """Return name of config file."""
    return pkg_name + "." + CONFIG_FILE_FORMAT


def get_global_config_path(pkg_name: str) -> Path:
    """Get name of global config path, with override from envvar."""
    # global configuration file directory can be overridden with this envvar
    config_dir_var = pkg_name.upper() + "_CONFIG_DIR"
    if config_dir_var in os.environ:
        return Path(os.environ[config_dir_var]).resolve()
    return Path(typer.get_app_dir(pkg_name))


def read_config(name: str, addl_config_dir: Union[None, str] = None) -> Any:
    """Reads a [merged] configuration file from a directory hierarchy.

    Configuration files will be merged from files in CONFIG_FILE_FORMAT
    from the following list of directories, in order:
        1. From the global config directory from get_global_config_path
        2. From the parent of the current working directory
        3. From the current working directory
        4. From the subdirectory addl_config_dir
    Merging requires the first line of the subsequent (non-global)
    config files to be:
        dynaconf_merge = true
    A copy of the default global config file will be copied from the
    template directory if the global config file does not exist.
    """
    name = name.lower()
    config_dir_path = get_global_config_path(name)
    try:
        config_dir_path.mkdir()
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    config_file_name = get_config_file_name(name.lower())
    global_config_path = config_dir_path / config_file_name
    logger.debug(f"Global config file at {global_config_path}")
    if not global_config_path.exists():
        logger.info(
            f"Creating config file {config_dir_path} from {name} template."
        )
        config_bytes = pkgutil.get_data(name, "templates/" + config_file_name)
        if config_bytes is not None:
            config_template = config_bytes.decode("utf-8")
            with global_config_path.open("w") as global_config_fp:
                global_config_fp.write(config_template)

    config_file_path_list = [global_config_path]
    pwd: Path = Path(".").resolve()
    config_file_path_list.append(pwd.parent / config_file_name)
    config_file_path_list.append(pwd / config_file_name)
    if addl_config_dir is not None:
        config_file_path_list.append(pwd / addl_config_dir / config_file_name)

    settings = Dynaconf(
        envvar_prefix=name,
        settings_files=config_file_path_list,
    )
    return settings
