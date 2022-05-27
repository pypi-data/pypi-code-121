"""Tests `bitfount/federated/encryption.py`."""
import base64
from pathlib import Path
import re
from typing import Optional
from unittest.mock import create_autospec

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.hashes import HashAlgorithm
import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.federated.encryption import (
    _AES_NONCE_SIZE_BYTES,
    _AESEncryption,
    _calc_max_RSA_message_size,
    _read_file,
    _RSAEncryption,
)
from bitfount.federated.exceptions import DecryptError
from tests.bitfount import TEST_SECURITY_FILES
from tests.utils.helper import (
    PRIVATE_KEY,
    PRIVATE_SSH_KEY,
    PUBLIC_KEY,
    PUBLIC_SSH_KEY,
    unit_test,
)

MAX_BYTE_VALUE = 255
PUBLIC_KEY_PATH = TEST_SECURITY_FILES / "test_public.testkey"


@unit_test
class TestEncryptionUtils:
    """Tests encryption utility functions."""

    def test_read_file(self) -> None:
        """Tests `read_file` returns bytes."""
        contents = _read_file(PUBLIC_KEY_PATH)
        assert contents is not None
        assert isinstance(contents, bytes)

    @pytest.mark.parametrize(
        argnames=("rsa_key_size_bits", "oaep_hash_algo", "expected_max_size"),
        argvalues=(
            # Taken from https://crypto.stackexchange.com/a/42100
            (1024, hashes.SHA1(), 86),
            (1024, hashes.SHA224(), 70),
            (1024, hashes.SHA256(), 62),
            (1024, hashes.SHA384(), 30),
            (2048, hashes.SHA1(), 214),
            (2048, hashes.SHA224(), 198),
            (2048, hashes.SHA256(), 190),
            (2048, hashes.SHA384(), 158),
            (2048, hashes.SHA512(), 126),
            (3072, hashes.SHA1(), 342),
            (3072, hashes.SHA224(), 326),
            (3072, hashes.SHA256(), 318),
            (3072, hashes.SHA384(), 286),
            (3072, hashes.SHA512(), 254),
            (4096, hashes.SHA1(), 470),
            (4096, hashes.SHA224(), 454),
            (4096, hashes.SHA256(), 446),
            (4096, hashes.SHA384(), 414),
            (4096, hashes.SHA512(), 382),
        ),
    )
    @pytest.mark.parametrize("private_or_public_key", (True, False))
    def test__calc_max_RSA_message_size(
        self,
        expected_max_size: int,
        mocker: MockerFixture,
        oaep_hash_algo: HashAlgorithm,
        private_or_public_key: bool,
        rsa_key_size_bits: int,
    ) -> None:
        """Tests max RSA message size calculator against known values."""
        # Create key mock with target size
        if private_or_public_key:
            mock_key = create_autospec(RSAPrivateKey, instance=True)
        else:
            mock_key = create_autospec(RSAPublicKey, instance=True)
        mock_key.key_size = rsa_key_size_bits

        # Patch out retrieval of OAEP digest size
        mock__get_encryption_padding = mocker.patch.object(
            _RSAEncryption,
            "_get_encryption_padding",
        )
        mock__get_encryption_padding.return_value._algorithm = oaep_hash_algo

        assert _calc_max_RSA_message_size(mock_key) == expected_max_size


@unit_test
class TestRSAEncryption:
    """Tests for RSAEncryption class."""

    @fixture
    def private_key_file(self) -> Path:
        """Returns private key file."""
        return TEST_SECURITY_FILES / "test_private.testkey"

    @fixture
    def private_key(self, private_key_file: Path) -> RSAPrivateKey:
        """Loaded private key from private key file."""
        return _RSAEncryption.load_private_key(private_key_file)

    @fixture
    def public_key_file(self) -> Path:
        """Returns public key file."""
        return TEST_SECURITY_FILES / "test_public.testkey"

    @fixture
    def public_key(self, public_key_file: Path) -> RSAPublicKey:
        """Loaded public key from public key file."""
        return _RSAEncryption.load_public_key(public_key_file)

    @fixture
    def public_key_size_bytes(self, public_key: RSAPublicKey) -> int:
        """Key size for public key fixture."""
        return (public_key.key_size + 7) // 8

    @fixture
    def signature_file(self) -> Path:
        """Returns signature file."""
        return TEST_SECURITY_FILES / "test_signature.sign"

    @fixture
    def private_key_bytes(self) -> bytes:
        """Returns private key bytes."""
        return PRIVATE_KEY.encode()

    @fixture
    def public_key_bytes(self) -> bytes:
        """Returns public key bytes."""
        return PUBLIC_KEY.encode()

    @fixture
    def private_ssh_key_file(self) -> Path:
        """Returns private ssh key file."""
        return TEST_SECURITY_FILES / "test_ssh_key_rsa.sshtestkey"

    @fixture
    def public_ssh_key_file(self) -> Path:
        """Returns public ssh key file."""
        return TEST_SECURITY_FILES / "test_ssh_key_rsa.pub.sshtestkey"

    @fixture
    def private_ssh_key_bytes(self) -> bytes:
        """Returns private ssh key bytes."""
        return PRIVATE_SSH_KEY.encode()

    @fixture
    def public_ssh_key_bytes(self) -> bytes:
        """Returns public ssh key bytes."""
        return PUBLIC_SSH_KEY.encode()

    def test_generate_key_pair_produces_rsa_keys(self) -> None:
        """Checks that an RSAPublicKey and an RSAPrivateKey are generated."""
        private_key, public_key = _RSAEncryption.generate_key_pair()

        assert private_key.key_size >= 2048

        assert isinstance(private_key, RSAPrivateKey)
        assert isinstance(public_key, RSAPublicKey)

    def test_load_public_key(
        self, public_key_bytes: bytes, public_key_file: Path
    ) -> None:
        """Tests loading of PEM public key from file and bytes."""
        public_key = _RSAEncryption.load_public_key(public_key_file)
        assert public_key is not None
        assert isinstance(public_key, RSAPublicKey)

        public_key = _RSAEncryption.load_public_key(public_key_bytes)
        assert public_key is not None
        assert isinstance(public_key, RSAPublicKey)

    def test_load_public_ssh_key(
        self, public_ssh_key_bytes: bytes, public_ssh_key_file: Path
    ) -> None:
        """Tests loading of SSH public key from file and bytes."""
        public_key = _RSAEncryption.load_public_key(public_ssh_key_file)
        assert public_key is not None
        assert isinstance(public_key, RSAPublicKey)

        public_key = _RSAEncryption.load_public_key(public_ssh_key_bytes)
        assert public_key is not None
        assert isinstance(public_key, RSAPublicKey)

    def test_serialized_and_deserialized_public_key_is_same_key(self) -> None:
        """Checks serialization and deserialization for PEM-format public keys."""
        _, public_key = _RSAEncryption.generate_key_pair()

        reloaded_key = _RSAEncryption.load_public_key(
            _RSAEncryption.serialize_public_key(public_key)
        )

        assert public_key.public_numbers() == reloaded_key.public_numbers()

    def test_load_private_key(
        self, private_key_bytes: bytes, private_key_file: Path
    ) -> None:
        """Tests loading of PEM private key from file and bytes."""
        private_key = _RSAEncryption.load_private_key(private_key_file)
        assert private_key is not None
        assert isinstance(private_key, RSAPrivateKey)

        private_key = _RSAEncryption.load_private_key(private_key_bytes)
        assert private_key is not None
        assert isinstance(private_key, RSAPrivateKey)

    def test_load_private_ssh_key(
        self, private_ssh_key_bytes: bytes, private_ssh_key_file: Path
    ) -> None:
        """Tests loading of SSH private key from file and bytes."""
        private_key = _RSAEncryption.load_private_key(private_ssh_key_file)
        assert private_key is not None
        assert isinstance(private_key, RSAPrivateKey)

        private_key = _RSAEncryption.load_private_key(private_ssh_key_bytes)
        assert private_key is not None
        assert isinstance(private_key, RSAPrivateKey)

    def test_serialized_and_deserialized_private_key_is_same_key(self) -> None:
        """Checks serialization and deserialization for PEM-format private keys."""
        private_key, _ = _RSAEncryption.generate_key_pair()

        reloaded_key = _RSAEncryption.load_private_key(
            _RSAEncryption.serialize_private_key(private_key)
        )

        assert private_key.private_numbers() == reloaded_key.private_numbers()

    def test_sign_message(self, private_key: RSAPrivateKey) -> None:
        """Tests message signing produces byte signatures."""
        message = b"Test*123"
        signature = _RSAEncryption.sign_message(private_key, message)
        assert signature is not None
        assert isinstance(signature, bytes)

    def test_verify_javascript_signed_signature(
        self, public_key: RSAPublicKey, signature_file: Path
    ) -> None:
        """Checks message signature verification using external values.

        Uses signatures and message from javascript tests.
        """
        message = "Test*123".encode("ascii")
        with open(signature_file, "r") as f:
            signature = f.readline().encode("ascii")
            signature = base64.b64decode(signature)
        result = _RSAEncryption.verify_signature(public_key, signature, message)
        assert result

    def test_verify_signature(
        self,
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey,
    ) -> None:
        """Checks message signature verification works."""
        message = b"Hello world"
        signature = _RSAEncryption.sign_message(private_key, message)
        result = _RSAEncryption.verify_signature(public_key, signature, message)
        assert result

        # Try again with a different message but same signature
        message = b"Goodbye world"
        result = _RSAEncryption.verify_signature(public_key, signature, message)
        assert result is False

    def test_rsa_correct_decryption(
        self,
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey,
    ) -> None:
        """Tests encryption-decryption cycle in RSAEncryption."""
        message = b"Hello world"
        ciphertext = _RSAEncryption.encrypt(message, public_key)

        # Assert Decryption is correct
        plaintext = _RSAEncryption.decrypt(ciphertext, private_key)
        assert message == plaintext

    def test_rsa_failed_decryption(
        self,
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey,
    ) -> None:
        """Checks decryption raises exception if incorrect ciphertext."""
        message = b"Hello world"
        ciphertext = _RSAEncryption.encrypt(message, public_key)

        ciphertext = bytearray(ciphertext)
        ciphertext[1] = MAX_BYTE_VALUE - ciphertext[1]
        ciphertext = bytes(ciphertext)

        with pytest.raises(
            DecryptError, match=re.escape("Unable to decrypt RSA-encrypted message.")
        ):
            _RSAEncryption.decrypt(ciphertext, private_key)

    def test_rsa_uses_hybrid_encryption_for_too_large_messages(
        self,
        mocker: MockerFixture,
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey,
    ) -> None:
        """Checks hybrid encryption used for too large messages."""
        # Wrap AES encryption so we can check it was used
        wrapped_aes = mocker.patch(
            "bitfount.federated.encryption._AESEncryption", wraps=_AESEncryption
        )

        # Make a message _just_ over the maximum size
        message = b"a" * (_calc_max_RSA_message_size(public_key) + 1)

        encrypted_message = _RSAEncryption.encrypt(message, public_key)
        decrypted_message = _RSAEncryption.decrypt(encrypted_message, private_key)

        assert decrypted_message == message

        # Check AES methods used
        wrapped_aes.generate_key.assert_called_once()
        wrapped_aes.encrypt.assert_called_once()
        wrapped_aes.decrypt.assert_called_once()

    @pytest.mark.parametrize(
        argnames=("invalidate_index_shift", "expected_error_msg"),
        argvalues=(
            pytest.param(
                None,
                "Unable to decrypt AES key in hybrid RSA-encrypted message.",
                id="aes_key_invalid",
            ),
            pytest.param(
                0,
                "Unable to decrypt ciphertext in hybrid RSA-encrypted message.",
                id="aes_nonce_invalid",
            ),
            pytest.param(
                _AES_NONCE_SIZE_BYTES,
                "Unable to decrypt ciphertext in hybrid RSA-encrypted message.",
                id="aes_ciphertext_invalid",
            ),
        ),
    )
    def test_hybrid_decryption_fails_with_incorrect_ciphertext(
        self,
        expected_error_msg: str,
        invalidate_index_shift: Optional[int],
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey,
        public_key_size_bytes: int,
    ) -> None:
        """Checks hybrid encryption fails if ciphertext incorrect.

        Due to a quirk of lazy_fixture (https://github.com/TvoroG/pytest-lazy-fixture/issues/24)  # noqa: B950
        we can't use that in the parameterization so instead use whether a shift
        is present or not to determine which base index we're working from.
        """
        # Make a message _just_ over the maximum size
        message = b"a" * (_calc_max_RSA_message_size(public_key) + 1)

        encrypted_message = _RSAEncryption.encrypt(message, public_key)

        # Modify message to invalid state
        if invalidate_index_shift is None:
            invalidate_index = 0
        else:
            invalidate_index = public_key_size_bytes + invalidate_index_shift
        encrypted_message = bytearray(encrypted_message)
        encrypted_message[invalidate_index] = (
            MAX_BYTE_VALUE - encrypted_message[invalidate_index]
        )
        encrypted_message = bytes(encrypted_message)

        with pytest.raises(DecryptError, match=re.escape(expected_error_msg)):
            _RSAEncryption.decrypt(encrypted_message, private_key)


@unit_test
class TestAESEncryption:
    """Tests AESEncryption class."""

    @fixture
    def key(self) -> bytes:
        """An AESEncryption key to use in tests."""
        return _AESEncryption.generate_key()

    @fixture
    def message(self) -> bytes:
        """Plaintext message to encrypt."""
        return b"Hello world"

    def test_aes_correct_encryption_decryption(
        self, key: bytes, message: bytes
    ) -> None:
        """Tests encryption-decryption cycle in AESEncryption."""
        ciphertext, nonce = _AESEncryption.encrypt(key, message)
        plaintext = _AESEncryption.decrypt(key, nonce, ciphertext)
        assert plaintext == message

    def test_aes_wrong_nonce_decryption(self, key: bytes, message: bytes) -> None:
        """Checks decryption raises error if incorrect nonce."""
        ciphertext, nonce = _AESEncryption.encrypt(key, message)
        wrong_nonce = bytes((MAX_BYTE_VALUE - i) for i in nonce)
        with pytest.raises(DecryptError):
            _AESEncryption.decrypt(key, wrong_nonce, ciphertext)

    def test_aes_failed_decryption(self, key: bytes, message: bytes) -> None:
        """Checks decryption raises error if incorrect ciphertext."""
        ciphertext, nonce = _AESEncryption.encrypt(key, message)
        ciphertext = bytearray(ciphertext)
        ciphertext[1] = MAX_BYTE_VALUE - ciphertext[1]
        ciphertext = bytes(ciphertext)
        with pytest.raises(
            DecryptError, match=re.escape("Unable to decrypt ciphertext")
        ):
            _AESEncryption.decrypt(key, nonce, ciphertext)
