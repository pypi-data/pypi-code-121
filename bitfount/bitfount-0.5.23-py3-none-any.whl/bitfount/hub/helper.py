"""Helper functions related to hub and AM interactions."""
import logging
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import yaml

from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    BITFOUNT_KEY_STORE,
    BITFOUNT_STORAGE_PATH,
    _get_environment,
)
from bitfount.data.schema import BitfountSchema
from bitfount.federated.encryption import _RSAEncryption
from bitfount.hub.api import (
    _DEV_AM_URL,
    _DEV_HUB_URL,
    _STAGING_AM_URL,
    _STAGING_HUB_URL,
    PRODUCTION_AM_URL,
    PRODUCTION_HUB_URL,
    BitfountAM,
    BitfountHub,
)
from bitfount.hub.authentication_flow import (
    _DEFAULT_USER_DIRECTORY,
    _DEVELOPMENT_AUTH_DOMAIN,
    _DEVELOPMENT_CLIENT_ID,
    _STAGING_AUTH_DOMAIN,
    _STAGING_CLIENT_ID,
    BitfountSession,
)
from bitfount.hub.exceptions import PodDoesNotExistError

logger = logging.getLogger(__name__)


def _create_bitfount_session(
    url: str, username: Optional[str] = None
) -> BitfountSession:
    """Creates a relevant Bitfount Session according to the environment.

    Args:
        url: Bitfount hub URL.
        username: Optional. Username. Defaults to DEFAULT_USER_DIRECTORY.

    Returns:
        BitfountSession object.
    """
    username = username if username else _DEFAULT_USER_DIRECTORY
    user_storage_path = BITFOUNT_STORAGE_PATH / username

    if url == _STAGING_HUB_URL:
        session = BitfountSession(
            _STAGING_AUTH_DOMAIN, _STAGING_CLIENT_ID, user_storage_path
        )
    elif "localhost" in url:
        session = BitfountSession(
            auth_domain=_DEVELOPMENT_AUTH_DOMAIN,
            client_id=_DEVELOPMENT_CLIENT_ID,
            user_storage_path=user_storage_path,
        )
    else:
        session = BitfountSession(user_storage_path=user_storage_path)

    return session


def _default_bitfounthub(
    hub: Optional[BitfountHub] = None,
    username: Optional[str] = None,
    url: Optional[str] = None,
) -> BitfountHub:
    """Gets a default BitfountHub instance if one is not specified.

    Args:
        hub: Optional. The BitfountHub instance to use if it exists.
        username: Optional. Username.
        url: Optional. Bitfount hub URL.

    Returns:
        BitfountHub object representing the hub.
    """
    if not hub:
        return _create_bitfounthub(username, url)
    return hub


def _create_bitfounthub(
    username: Optional[str] = None, url: Optional[str] = None
) -> BitfountHub:
    """Creates bitfounthub object.

    Args:
        username: Optional. Username.
        url: Optional. Bitfount hub URL. Will use the environment default if not
             supplied.

    Returns:
        BitfountHub object representing the hub.
    """
    if not url:
        environment = _get_environment()
        if environment == _STAGING_ENVIRONMENT:
            url = _STAGING_HUB_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            url = _DEV_HUB_URL
        else:
            url = PRODUCTION_HUB_URL
    session = _create_bitfount_session(url=url, username=username)
    session.authenticate()
    return BitfountHub(session=session, url=url)


def _create_access_manager(
    session: BitfountSession, url: Optional[str] = None
) -> BitfountAM:
    """Creates and returns Bitfount Access Manager.

    Args:
        session: Bitfount session for authentication.
        url: Optional. URL of the access manager. Will use the environment default
             if not supplied.

    Returns:
        The BitfountAM representing the access manager.
    """
    if not url:
        environment = _get_environment()
        if environment == _STAGING_ENVIRONMENT:
            url = _STAGING_AM_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            url = _DEV_AM_URL
        else:
            url = PRODUCTION_AM_URL

    return BitfountAM(session, url)


def _get_access_manager_public_key(session: BitfountSession) -> RSAPublicKey:
    """Creates access manager and returns corresponding public key.

    Args:
        session: Bitfount session for authenticated HTTP calls.

    Returns:
        The access manager's public key.
    """
    access_manager = _create_access_manager(session)
    return access_manager.get_access_manager_key()


def _save_key_to_key_store(
    key_store_path: Path, pod_identifier: str, serialized_pod_key: str
) -> None:
    """Save new pod keys to the key store.

    Args:
        key_store_path: The path to where the key files are stored
        pod_identifier: The pod identifier of the pod we are saving the key for.
        serialized_pod_key: The serialized pod key
    """
    with open(key_store_path, "r") as key_store:
        known_pod_keys: Dict[str, str] = yaml.safe_load(key_store) or {}

    known_pod_keys[pod_identifier] = serialized_pod_key

    with open(key_store_path, "w") as key_store:
        logger.debug(f"Saving pod public keys to {key_store_path}")
        yaml.safe_dump(known_pod_keys, key_store)


def _check_known_pods(
    pod_name: str, pod_public_key: RSAPublicKey, key_store_path: Path
) -> RSAPublicKey:
    """Checks known pods still have valid public key.

    Checks pod public key is the same as in BITFOUNT_KEY_STORE
    If BITFOUNT_KEY_STORE does not exist, it creates it and adds the key
    If it does exist but the key is different, it prompts the user to
    accept or reject new key.

    Returns:
        The new or existing key (depending on which the user chooses) as a string.
    """
    # Check whether the provided key matches the existing key, request permission
    # to update if not.
    serialized_pod_key: str = _RSAEncryption.serialize_public_key(
        pod_public_key
    ).decode()
    with open(key_store_path, "r") as key_store:
        known_pod_keys: Dict[str, str] = yaml.safe_load(key_store) or {}
        serialized_current_pod_key: Optional[str] = known_pod_keys.get(pod_name, None)

        if serialized_current_pod_key is None:
            # No current key for this user, ok to "update" it
            logger.debug(f"No existing key found for pod {pod_name}")
        elif serialized_current_pod_key != serialized_pod_key:
            logger.error(
                f"{pod_name} public key has changed. \n"
                f"Please double check the key has really changed and this "
                f"is not an attack."
            )
            while True:
                # We are only using python3 so this is secure
                response = input(  # nosec
                    "Do you want to trust the new public key? (y/n)"
                )
                if response.lower() == "y":
                    # Break out of the loop
                    break
                elif response.lower() == "n":
                    # Use the old public key
                    return _RSAEncryption.load_public_key(
                        serialized_current_pod_key.encode()
                    )
                else:
                    print("Didn't catch that, please type 'y' or 'n'")

    # Save known pod key with the new one. We do this here because either
    # the user has approved or there was no key for that user in the first
    # place.
    _save_key_to_key_store(key_store_path, pod_name, serialized_pod_key)

    logger.info(f"Found public key for {pod_name} in key store.")
    # The new pod key has been saved so we can just return it
    return pod_public_key


def _get_pod_public_key(
    pod_identifier: str,
    hub: BitfountHub,
    pod_public_key_paths: Optional[Mapping[str, Path]] = None,
) -> RSAPublicKey:
    """Gets a pod's public key.

    Either loads it from disk or downloads it from BitfountHub.

    Args:
        pod_identifier: The pod identifier of the pod we get the public key for.
        hub: Hub to download keys from.
        pod_public_key_paths: Optional. Mapping of pod identifiers to already
            existing keys.

    Returns:
        The public key for the pod.

    Raises:
        PodDoesNotExistError: If the pod does not exist.
    """
    key_store_path = Path(BITFOUNT_KEY_STORE).expanduser()

    # Create key store file if file doesn't exist
    if not key_store_path.is_file():
        logger.info("Creating key store for pod public keys...")
        key_store_path.parent.mkdir(parents=True, exist_ok=True)
        key_store_path.touch()

    if pod_public_key_paths:
        logger.info(f"Checking if we already have the public key for {pod_identifier}")
        try:
            pod_public_key_path: Path = pod_public_key_paths[pod_identifier]
            existing_pod_public_key = _RSAEncryption.load_public_key(
                pod_public_key_path
            )
            return _check_known_pods(
                pod_identifier, existing_pod_public_key, key_store_path
            )
        except KeyError:
            # We have some pod public key files, but not for this pod identifier
            logger.debug(f"No existing public key file for {pod_identifier}")

    # If no key files at all, or just not for that pod, retrieve it
    if pod_key := hub.get_pod_key(pod_identifier=pod_identifier):
        pod_public_key = _RSAEncryption.load_public_key(pod_key.encode())
        serialized_pod_key: str = _RSAEncryption.serialize_public_key(
            pod_public_key
        ).decode()

        # Save out the keys
        _save_key_to_key_store(key_store_path, pod_identifier, serialized_pod_key)

        return pod_public_key
    else:
        raise PodDoesNotExistError(f"No public key found for pod: {pod_identifier}")


def _get_pod_public_keys(
    pod_identifiers: Iterable[str],
    hub: BitfountHub,
    pod_public_key_paths: Optional[Mapping[str, Path]] = None,
) -> Dict[str, RSAPublicKey]:
    """Retrieve the public keys for a group of pods.

    Either loads it from disk or downloads it from BitfountHub.

    Args:
        pod_identifiers: The pod identifiers of the pods we want the public keys for.
        hub: Hub to download keys from.
        pod_public_key_paths: Optional. Mapping of pod identifiers to already
                              existing keys.

    Returns:
        A dictionary of pod identifiers to the public key for that pod.
    """
    # Either download public key, or load existing, for each pod
    loaded_pod_public_keys: Dict[str, RSAPublicKey] = {
        pod_identifier: _get_pod_public_key(pod_identifier, hub, pod_public_key_paths)
        for pod_identifier in pod_identifiers
    }
    return loaded_pod_public_keys


def get_pod_schema(
    pod_identifier: str,
    save_file_path: Optional[Union[str, Path]] = None,
    hub: Optional[BitfountHub] = None,
    username: Optional[str] = None,
) -> BitfountSchema:
    """Get a pod's schema from the hub.

    Args:
        pod_identifier: The identifier of the pod. If supplied with only pod name
            assumes the namespace is the current user.
        save_file_path: Optional. Path to save the downloaded schema to. Won't save
            if not provided.
        hub: Optional. The BitfountHub to connect to. The default hub will be
             used if not provided.
        username: The username to use when connecting to the hub if a hub instance is
            not provided.

    Returns:
        The loaded BitfountSchema object.
    """
    # Generate default hub if not provided
    if not hub:
        hub = _create_bitfounthub(username=username)
    elif username:
        logger.warning("Ignoring username argument as hub was provided.")

    # Check if full pod_identifier or pod name only
    if "/" not in pod_identifier:
        # Construct full pod identifier if needed
        pod_identifier = f"{hub.username}/{pod_identifier}"

    schema = hub.get_pod_schema(pod_identifier)

    # Save out schema if requested
    if save_file_path:
        schema.dump(Path(save_file_path).expanduser())
    return schema
