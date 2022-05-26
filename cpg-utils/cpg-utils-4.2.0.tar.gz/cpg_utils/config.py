"""Provides access to config variables."""

import os
from typing import Any, MutableMapping, Optional
from cloudpathlib import AnyPath
import toml

# We use these globals for lazy initialization, but pylint doesn't like that.
# pylint: disable=global-statement, invalid-name
_config_path = os.getenv('CPG_CONFIG_PATH')  # See set_config_path.
_config: Optional[MutableMapping[str, Any]] = None  # Cached config, initialized lazily.


def set_config_path(config_path: str) -> None:
    """Sets the config path that's used by subsequent calls to get_config.

    If this isn't called, the value of the CPG_CONFIG_PATH environment variable is used
    instead.

    Parameters
    ----------
    config_path: str
        A cloudpathlib-compatible path to a TOML file containing the configuration.
    """

    global _config_path, _config
    if _config_path != config_path:
        _config_path = config_path
        _config = None  # Make sure the config gets reloaded.


def get_config() -> MutableMapping[str, Any]:
    """Returns the configuration dictionary.

    Call set_config_path beforehand to override the default path.

    Examples
    --------
    Here's a typical configuration file in TOML format:

    [hail]
    billing_project = "tob-wgs"
    bucket = "cpg-tob-wgs-hail"

    [workflow]
    access_level = "test"
    dataset = "tob-wgs"
    dataset_gcp_project = "tob-wgs"
    driver_image = "australia-southeast1-docker.pkg.dev/analysis-runner/images/driver:36c6d4548ef347f14fd34a5b58908057effcde82-hail-ad1fc0e2a30f67855aee84ae9adabc3f3135bd47"
    image_registry_prefix = "australia-southeast1-docker.pkg.dev/cpg-common/images"
    reference_prefix = "gs://cpg-reference"
    output_prefix = "plasma/chr22/v6"

    >>> from cpg_utils.config import get_config
    >>> get_config()['workflow']['dataset']
    'tob-wgs'

    Notes
    -----
    Caches the result based on the config path alone.

    Returns
    -------
    MutableMapping[str, Any]
    """

    global _config
    if _config is None:  # Lazily initialize the config.
        assert (
            _config_path
        ), 'Either set the CPG_CONFIG_PATH environment variable or call set_config_path'

        with AnyPath(_config_path).open() as f:
            config_str = f.read()

        # Print the config content, which is helpful for debugging.
        print(f'Configuration at {_config_path}:\n{config_str}')
        _config = toml.loads(config_str)

    return _config
