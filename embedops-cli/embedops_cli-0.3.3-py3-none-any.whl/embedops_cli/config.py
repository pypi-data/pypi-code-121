"""This module provides a central store for configuration data, drawing from environment variables
configuration files, and other sources as needed"""
import os
from dynaconf import Dynaconf

SETTINGS_FILES = ["settings.toml", ".secrets.toml"]

# get an absolute path to the director that this file is in
abs_current_dir = os.path.dirname(os.path.abspath(__file__))

# prepend the settings filenames with an absolute path to the current directory
# by providing an absolute path, dynaconf will load it directly instead of
# searching for it
settings_paths = [
    os.path.join(abs_current_dir, settings_file) for settings_file in SETTINGS_FILES
]

settings = Dynaconf(
    load_dotenv=True,
    envvar_prefix="EMBEDOPS",
    environments=True,
    settings_files=settings_paths,
)

# for some reason, we have to set the loaders separately to be able to use `.configure` to
# change them for tests
settings.configure(
    LOADERS_FOR_DYNACONF=[
        "dynaconf.loaders.yaml_loader",
        "dynaconf.loaders.env_loader",
        "embedops_cli.ci_config_loader",
    ]
)
