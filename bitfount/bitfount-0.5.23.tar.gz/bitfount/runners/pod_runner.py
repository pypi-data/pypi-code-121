"""Contains courtesy classes and functions for making pod running easier."""
import importlib
import logging
import os
from os import PathLike
from typing import Union

import desert
from envyaml import EnvYAML

from bitfount.federated.pod import Pod
from bitfount.federated.pod_keys_setup import _get_pod_keys
from bitfount.hub.helper import _create_access_manager, _create_bitfounthub
from bitfount.runners.config_schemas import PodConfig

logger = logging.getLogger(__name__)


def setup_pod_from_config_file(path_to_config_yaml: Union[str, PathLike]) -> Pod:
    """Creates a pod from a YAML config file.

    Args:
        path_to_config_yaml: The path to the config file.

    Returns:
        The created pod.
    """
    logger.debug(f"Loading pod config from: {path_to_config_yaml}")
    config_yaml = EnvYAML._EnvYAML__read_yaml_file(
        path_to_config_yaml, os.environ, strict=True
    )
    config = desert.schema(PodConfig).load(config_yaml)
    return setup_pod_from_config(config)


def setup_pod_from_config(config: PodConfig) -> Pod:
    """Creates a pod from a loaded config.

    Args:
        config: The configuration as a PodConfig instance.

    Returns:
        The created pod.
    """
    bitfount_hub = _create_bitfounthub(config.username, config.hub.url)
    access_manager = _create_access_manager(
        bitfount_hub.session, config.access_manager.url
    )

    # Load Pod Keys
    pod_directory = bitfount_hub.user_storage_path / "pods" / config.pod_name
    pod_keys = _get_pod_keys(pod_directory)

    try:
        datasource_cls = getattr(importlib.import_module("bitfount"), config.datasource)
    except AttributeError:
        raise ImportError(f"Unable to import {config.datasource} from bitfount.")
    datasource = datasource_cls(**config.data_config.datasource_args)

    return Pod(
        name=config.pod_name,
        datasource=datasource,
        schema=config.schema,
        data_config=config.data_config,
        pod_details_config=config.pod_details,
        bitfounthub=bitfount_hub,
        ms_config=config.message_service,
        access_manager=access_manager,
        pod_keys=pod_keys,
        approved_pods=config.other_pods,
    )
