"""Symmetric and asymmetric encryption functions."""
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Final, Optional, Tuple, Union, cast

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPrivateKeyWithSerialization,
    RSAPublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from bitfount.federated.exceptions import DecryptError
from bitfount.federated.logging import _get_federated_logger

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.padding import MGF
    from cryptography.hazmat.primitives.hashes import HashAlgorithm


logger = _get_federated_logger(__name__)

# RSA Constants
_RSA_PUBLIC_EXPONENT: Final[int] = 65537
_RSA_KEY_SIZE_BITS: Final[int] = 4096
# Salt length is padding.PSS.MAX_LENGTH, but we manually set it to ensure
# compatibility across platforms.
_RSA_SIGN_SALT_LENGTH: Final[int] = 20

# AES Constants
# The AES key must provide at least as much security as the RSA key as they are
# both used in hybrid encryption (when the message is too large for RSA encryption
# alone).
#
# This NIST-based table allows us to find values which will enable that:
#   https://www.keylength.com/en/4/
_AES_KEY_SIZE_BITS: Final[int] = 256
_AES_NONCE_SIZE_BYTES: Final[int] = 12


def _read_file(file_to_read: Path) -> bytes:
    """Reads given file and returns contents as a byte string."""
    with open(file_to_read, "rb") as f:
        contents = f.read()
    return contents


def _calc_max_RSA_message_size(rsa_key: Union[RSAPrivateKey, RSAPublicKey]) -> int:
    """Calculates the maximum message size that can be encrypted.

    Calculates the maximum message size, in bytes, that can be encrypted with
    the supplied key.

    https://www.rfc-editor.org/rfc/rfc8017#section-7.1.1
    """
    # This is the approach used internally to cryptography
    # Rounded up byte-size from bit-size
    rsa_key_size_bytes = (rsa_key.key_size + 7) // 8

    # Get the expected padding settings and access the algorithm to get the
    # expected output size.
    oaep_hash_output_size_bytes = (
        _RSAEncryption._get_encryption_padding()._algorithm.digest_size
    )

    # Equation from: https://www.rfc-editor.org/rfc/rfc8017#section-7.1.1
    max_size = rsa_key_size_bytes - (2 * oaep_hash_output_size_bytes) - 2
    return max_size


class _RSAEncryption:
    """Class of functions for dealing with RSA asymmetric encryption."""

    @staticmethod
    def generate_key_pair() -> Tuple[RSAPrivateKey, RSAPublicKey]:
        """Generates a new RSA key pair."""
        logger.debug("Generating RSA key pair")
        # Key size is 4096 bits which means we can only encrypt up to 4096 bits of data
        private_key = rsa.generate_private_key(
            public_exponent=_RSA_PUBLIC_EXPONENT,
            key_size=_RSA_KEY_SIZE_BITS,
            backend=default_backend(),
        )
        return private_key, private_key.public_key()

    @staticmethod
    def load_private_key(private_key: Union[bytes, Path]) -> RSAPrivateKey:
        """Loads a private key either from a byte string or file path."""
        logger.debug("Attempting to load private key")
        if isinstance(private_key, Path):
            logger.debug(f"Loading private key from path: {private_key}")
            private_key = _read_file(private_key)

        # Try loading from PEM format first
        try:
            logger.debug("Attempting to load private key using PEM Format...")
            loaded_private_key = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )

        except ValueError as ve:
            # Otherwise try SSH format
            try:
                logger.debug(
                    "Loading private key using PEM format failed,"
                    " trying to load using SSH format..."
                )
                loaded_private_key = serialization.load_ssh_private_key(
                    private_key, password=None, backend=default_backend()
                )
            except ValueError:
                # If both fail, raise the original error
                raise ve

        logger.debug("Loaded private key")
        return cast(RSAPrivateKey, loaded_private_key)

    @staticmethod
    def serialize_private_key(private_key: RSAPrivateKeyWithSerialization) -> bytes:
        """Serializes a private key to bytes."""
        return private_key.private_bytes(
            Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
        )

    @staticmethod
    def load_public_key(public_key: Union[bytes, Path]) -> RSAPublicKey:
        """Loads a public key either from a byte string or file path."""
        logger.debug("Attempting to load public key")
        if isinstance(public_key, Path):
            logger.debug(f"Loading public key from path: {public_key}")
            public_key = _read_file(public_key)

        # Try loading from PEM format first
        try:
            logger.debug("Attempting to load public key using PEM Format...")
            loaded_public_key = serialization.load_pem_public_key(
                public_key, backend=default_backend()
            )
        except ValueError as ve:
            # Otherwise try SSH format
            try:
                logger.debug(
                    "Loading public key using PEM format failed, "
                    "trying to load using SSH format..."
                )
                loaded_public_key = serialization.load_ssh_public_key(
                    public_key, backend=default_backend()
                )
            except ValueError:
                # If both fail, raise the original error
                raise ve

        logger.debug("Loaded public key")
        return cast(RSAPublicKey, loaded_public_key)

    @staticmethod
    def serialize_public_key(public_key: RSAPublicKey) -> bytes:
        """Serialize an RSAPublicKey to bytes."""
        return public_key.public_bytes(Encoding.PEM, PublicFormat.PKCS1)

    @staticmethod
    def _get_hashing_algorithm() -> HashAlgorithm:
        """Retrieves a new instance representing the chosen hash algorithm."""
        return hashes.SHA256()

    @staticmethod
    def _get_mask_gen_function() -> MGF:
        """Retrieves a new instance representing the chosen mask generator function."""
        return padding.MGF1(_RSAEncryption._get_hashing_algorithm())

    @staticmethod
    def _get_signature_padding() -> padding.PSS:
        """Retrieves a new instance representing the padding algo for signatures."""
        return padding.PSS(
            mgf=_RSAEncryption._get_mask_gen_function(),
            salt_length=_RSA_SIGN_SALT_LENGTH,
        )

    @staticmethod
    def _get_encryption_padding() -> padding.OAEP:
        """Retrieves a new instance representing the padding algo for encryption."""
        return padding.OAEP(
            mgf=_RSAEncryption._get_mask_gen_function(),
            algorithm=_RSAEncryption._get_hashing_algorithm(),
            label=None,
        )

    @staticmethod
    def sign_message(private_key: RSAPrivateKey, message: bytes) -> bytes:
        """Cryptographically signs a message.

        Signs provided `message` with provided `private_key` and returns signature.
        """
        signature = private_key.sign(
            message,
            padding=_RSAEncryption._get_signature_padding(),
            algorithm=_RSAEncryption._get_hashing_algorithm(),
        )

        return signature

    @staticmethod
    def verify_signature(
        public_key: RSAPublicKey, signature: bytes, message: bytes
    ) -> bool:
        """Verifies that decrypting `signature` with `public_key` === `message`."""
        try:
            public_key.verify(
                signature,
                message,
                padding=_RSAEncryption._get_signature_padding(),
                algorithm=_RSAEncryption._get_hashing_algorithm(),
            )
        except InvalidSignature:
            return False

        logger.debug("Signature verified")
        return True

    @staticmethod
    def encrypt(message: bytes, public_key: RSAPublicKey) -> bytes:
        """Encrypts plaintext.

        Encrypts provided `message` with `public_key` and returns ciphertext.
        """
        # If message is small enough to be fully RSA encrypted then do that.
        if len(message) <= _calc_max_RSA_message_size(public_key):
            ciphertext = public_key.encrypt(
                message,
                _RSAEncryption._get_encryption_padding(),
            )
        # Otherwise, use hybrid encryption.
        else:
            logger.debug(
                "Message too large for RSA encryption, using hybrid encryption."
            )

            # Encrypt message with AES key
            aes_key = _AESEncryption.generate_key()
            aes_ciphertext, aes_nonce = _AESEncryption.encrypt(aes_key, message)

            # Encrypt AES key using RSA encryption
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                _RSAEncryption._get_encryption_padding(),
            )

            # Combine
            ciphertext = encrypted_aes_key + aes_nonce + aes_ciphertext
        return ciphertext

    @staticmethod
    def decrypt(
        ciphertext: bytes,
        private_key: RSAPrivateKey,
    ) -> bytes:
        """Decrypts ciphertext.

        Decrypts provided `ciphertext` with `private_key` and returns plaintext.

        Raises:
            DecryptError: if decryption fails.
        """
        # This is the approach used internally to cryptography
        # Rounded up byte-size from bit-size
        rsa_encrypted_size = (private_key.key_size + 7) // 8

        # If message is the expected RSA size then must have been purely RSA
        # encrypted. Decrypt directly.
        if len(ciphertext) <= rsa_encrypted_size:
            try:
                plaintext = private_key.decrypt(
                    ciphertext,
                    _RSAEncryption._get_encryption_padding(),
                )
            except ValueError:
                raise DecryptError("Unable to decrypt RSA-encrypted message.")
        # Otherwise, it must have been encrypted using hybrid encryption.
        else:
            logger.debug(
                "Message too large for RSA encryption, using hybrid decryption."
            )

            # Split received message into relevant parts.
            encrypted_aes_key, aes_payload = (
                ciphertext[:rsa_encrypted_size],
                ciphertext[rsa_encrypted_size:],
            )
            aes_nonce, aes_ciphertext = (
                aes_payload[:_AES_NONCE_SIZE_BYTES],
                aes_payload[_AES_NONCE_SIZE_BYTES:],
            )

            # Decrypt AES key
            try:
                aes_key = private_key.decrypt(
                    encrypted_aes_key,
                    _RSAEncryption._get_encryption_padding(),
                )
            except ValueError:
                raise DecryptError(
                    "Unable to decrypt AES key in hybrid RSA-encrypted message."
                )

            # Decrypt message body
            try:
                plaintext = _AESEncryption.decrypt(aes_key, aes_nonce, aes_ciphertext)
            except DecryptError:
                raise DecryptError(
                    "Unable to decrypt ciphertext in hybrid RSA-encrypted message."
                )

        return plaintext


class _AESEncryption:
    """Class of functions for dealing with AES symmetric encryption."""

    @staticmethod
    def generate_key() -> bytes:
        """Generates a symmetric encryption key.

        Generates symmetric key using the GCM algorithm (Galois Counter Mode).

        (More secure than CBC (Cipher Block Chaining)).
        """
        key = AESGCM.generate_key(
            bit_length=_AES_KEY_SIZE_BITS
        )  # 128 bits is sufficiently secure
        return key

    @staticmethod
    def encrypt(
        key: bytes, plaintext: bytes, associated_data: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """Encrypts plaintext.

        Encrypts `plaintext` using `key` and a randomly generated `nonce`.
        If `associated_data` is provided, it is authenticated.
        """
        aesgcm = AESGCM(key)
        nonce = os.urandom(_AES_NONCE_SIZE_BYTES)  # 12 bytes
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

        return ciphertext, nonce

    @staticmethod
    def decrypt(
        key: bytes,
        nonce: bytes,
        ciphertext: bytes,
        associated_data: Optional[bytes] = None,
    ) -> bytes:
        """Decrypts ciphertext.

        Decrypts `ciphertext` using `key`, `nonce` and `associated_data` if present.

        If `associated_data` is provided, this must be the same associated data
        used in encryption.

        ***
        NONCE MUST ONLY BE USED ONCE FOR A GIVEN KEY (SAME NONCE AS USED FOR
        ENCRYPTION)
        ***

        Raises:
            DecryptError: if decryption fails.
        """
        aesgcm = AESGCM(key)

        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
        except InvalidTag:
            raise DecryptError("Unable to decrypt ciphertext")

        return plaintext
