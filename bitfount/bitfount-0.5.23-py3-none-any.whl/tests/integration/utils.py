"""Utility functions for end-to-end testing."""
from collections import defaultdict
import inspect
import logging
from multiprocessing import current_process
import os
from pathlib import Path
from queue import Queue
import tempfile
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
import desert
import yaml

from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.modeller import _Modeller
from bitfount.federated.pod import Pod
from bitfount.runners.config_schemas import ModellerConfig, PathConfig, PodConfig
from bitfount.runners.modeller_runner import DEFAULT_MODEL_OUT, run_modeller

logger = logging.getLogger(__name__)


def load_pod_config(config_path: Path, data_path: Path) -> PodConfig:
    """Loads a pod config and fixes up.

    Loads a pod config file, performing the necessary dynamic suffixing and
    envvar loading.
    """
    # Load base config
    with open(config_path) as f:
        config_yaml = yaml.safe_load(f)
    config: PodConfig = desert.schema(PodConfig).load(config_yaml)

    suffix = str(int(time.time()))  # unix timestamp

    # Add suffix where needed
    config.pod_name += suffix
    config.pod_details.display_name += suffix
    if config.data_config.force_stypes:
        updated_force_stypes = {}
        for table_name in config.data_config.force_stypes:
            updated_force_stypes[
                f"{table_name}{suffix}"
            ] = config.data_config.force_stypes[table_name]
        config.data_config.force_stypes = updated_force_stypes
    # Update data
    config.data_config.datasource_args["path"] = PathConfig(data_path).path

    return config


def password_from_pod_config(config: PodConfig) -> str:
    """Get the user's hub password using the information in config."""
    return os.environ[f"{config.username}_pswd"]


def load_modeller_config(
    config_path: Path, private_key: Optional[RSAPrivateKey] = None
) -> ModellerConfig:
    """Loads modeller config and fixes up.

    Loads a modeller config file, performing the necessary dynamic suffixing,
    envvar loading, and private key substitution.
    """
    # Load base config
    with open(config_path) as f:
        config_yaml = yaml.safe_load(f)
    config: ModellerConfig = desert.schema(ModellerConfig).load(config_yaml)

    if not private_key:
        # Load appropriate private key from secrets onto the config
        private_key_str: str = os.environ[f"{config.modeller.username}_privkey"]
        private_key = _RSAEncryption.load_private_key(private_key_str.encode())
    config = _load_private_key_to_modeller_config(config, private_key)

    return config


def _load_private_key_to_modeller_config(
    config: ModellerConfig, private_key: RSAPrivateKey
) -> ModellerConfig:
    """Loads the private key as a file on the config.

    The caller is responsible for deleting the temporary file created.
    """
    # Create location for private key file. This is done separately to loading
    # the config because the key itself needs to be provided to write out to file
    # but we need the config to be loaded to extract the username.
    private_key_file = tempfile.NamedTemporaryFile(delete=False)
    private_key_file.write(_RSAEncryption.serialize_private_key(private_key))
    private_key_file.close()  # so can open it again later
    config.modeller.private_key_file = Path(private_key_file.name)
    return config


def password_from_modeller_config(config: ModellerConfig) -> str:
    """Get the modeller's hub password using the information in config."""
    return os.environ[f"{config.modeller.username}_pswd"]


def tie_together_configs(
    modeller_config: ModellerConfig, *pod_configs: PodConfig
) -> None:
    """Tie a set of modeller configs and pod configs with dynamic names together."""
    # Attach pods to modeller pod_names
    pod_ids = [p.pod_id for p in pod_configs]
    modeller_config.pods.identifiers = pod_ids

    # Attach pods to each others' "other_pods"
    for pod in pod_configs:
        other_pods = [p.pod_id for p in pod_configs if p is not pod]
        pod.other_pods = other_pods


def get_caplog_records(queue: Queue) -> Dict[str, List[str]]:
    """Returns caplog records as dictionary of levels and messages."""
    records: Dict[str, List[str]] = defaultdict(list)
    while not queue.empty():
        record = queue.get()
        records[record.levelname].append(record.message)
    return records


def pod_start(pod: Pod) -> None:
    """Helper function for running pod in a separate process.

    Fails tests if there are any errors.
    """
    try:
        pod.start()
    except Exception as e:
        logger.error(f"Caught exception in {current_process().name} process: {e}")
        raise e


def run_modeller_process(
    modeller: _Modeller,
    pod_identifiers: Iterable[str],
    model_out: Path = DEFAULT_MODEL_OUT,
    queue: Optional[Queue] = None,
) -> Optional[Any]:
    """Helper function for sending Modeller requests and running training.

    Helper function for sending modeller training requests and running training
    in a separate process and failing test if there are any errors.

    Args:
        modeller (Modeller):T he Modeller instance being used to manage the task.
        pod_identifiers (List[str]): List of pod identifiers to run the task against.
        model_out (Path): The path to save the model out to.
        queue (Queue): Optional queue to store output from running modeller process
    """
    try:
        res = run_modeller(modeller, pod_identifiers, model_out)
        if res and queue:
            queue.put(res)
        return res
    except Exception as e:
        logger.error(f"Caught exception in {current_process().name} process: {e}")
        raise e


def _mock_authentication_code(
    username: str, password: str, token_dir: Path
) -> Tuple[Any, Any]:
    """Returns mocks for BitfountSession and OIDC authentication flow.

    Args:
        username (str): username
        password (str): password
        token_dir (Path): path to where `.token` file should be stored
    """
    oidc_webbrowser_import = (
        "bitfount.federated.transport.identity_verification"
        ".oidc.webbrowser.open_new_tab"
    )
    from functools import partial
    from pathlib import Path
    from unittest.mock import patch

    from tests.integration.bitfount_web_interactions import (
        get_bitfount_session,
        oidc_flow,
    )

    session_patcher = patch(
        "bitfount.hub.helper.BitfountSession",
        return_value=get_bitfount_session(
            username,
            password,
            Path(str(token_dir)),
        ),
    )
    oidc_patcher = patch(
        oidc_webbrowser_import,
        side_effect=partial(
            oidc_flow,
            username=username,
            password=password,
        ),
    )
    return session_patcher, oidc_patcher


def mock_authentication_code_nb(username: str, password: str, token_dir: Path) -> str:
    """Returns code strinh for mocking out authentication flow.

    Mocks out BitfountSession as well as OIDC flow.

    Args:
        username (str): username
        password (str): password
        token_dir (Path): path to where `.token` file should be stored
    """
    mock_auth_code = inspect.getsource(_mock_authentication_code)
    ext = (
        "session_patcher, oidc_patcher = _mock_authentication_code("
        f"'{username}', '{password}', "
        f"'{str(token_dir)}')\n"
        f"user_storage_path = Path('{str(token_dir)}')/'pods'\n"
        "session_patcher.start()\n"
        "oidc_patcher.start()\n"
    )
    mock_auth_code = mock_auth_code + ext
    return mock_auth_code
