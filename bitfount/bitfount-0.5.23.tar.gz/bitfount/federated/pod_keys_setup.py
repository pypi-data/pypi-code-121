"""Module for setting up the pod keys."""
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives._serialization import Encoding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import PublicFormat

from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.logging import _get_federated_logger

PRIVATE_KEY_FILE = "pod_rsa.pem"
PUBLIC_KEY_FILE = "pod_rsa.pub.pem"


logger = _get_federated_logger(__name__)


@dataclass
class PodKeys:
    """A public-private key pair for a `Pod`.

    Args:
        public_key: The public key.
        private_key: The private key.
    """

    public: RSAPublicKey
    private: RSAPrivateKey


def _generate_key_pair(private_key_path: Path, public_key_path: Path) -> PodKeys:
    """Generates, saves and returns an RSA key pair.

    Args:
        private_key_path: the path to save the private key to
        public_key_path: the path to save the public key to

    Returns:
        A tuple of (private key, public key)
    """
    private_key_path.parent.mkdir(exist_ok=True, parents=True)
    public_key_path.parent.mkdir(exist_ok=True, parents=True)

    private_key, public_key = _RSAEncryption.generate_key_pair()

    private_key_path.write_bytes(_RSAEncryption.serialize_private_key(private_key))
    public_key_path.write_bytes(
        public_key.public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
    )
    return PodKeys(private=private_key, public=public_key)


def _load_key_pair(private_key_path: Path, public_key_path: Path) -> PodKeys:
    """Loads an existing RSA key pair.

    Args:
        private_key_path: the path to load the private key from
        public_key_path: the path to load the public key from

    Returns:
        A tuple of (private key, public key)
    """
    bytes_ = public_key_path.read_bytes()
    public_key = serialization.load_ssh_public_key(bytes_, default_backend())
    private_key = serialization.load_pem_private_key(
        private_key_path.read_bytes(), password=None, backend=default_backend()
    )

    # Reassure mypy
    public_key = cast(RSAPublicKey, public_key)
    private_key = cast(RSAPrivateKey, private_key)

    return PodKeys(public=public_key, private=private_key)


def _get_pod_keys(key_directory: Path) -> PodKeys:
    """Gets the encryption key pair for the pod.

    Get the pod keys from the target directory, generating them if they don't
    already exist.

    Args:
        key_directory: the directory where the keys are located or should be saved

    Returns:
        A tuple of (private key, public key)
    """
    private_key_path = key_directory / PRIVATE_KEY_FILE
    public_key_path = key_directory / PUBLIC_KEY_FILE
    if private_key_path.exists() and public_key_path.exists():
        pod_keys = _load_key_pair(private_key_path, public_key_path)
    else:
        pod_keys = _generate_key_pair(private_key_path, public_key_path)
    return pod_keys
