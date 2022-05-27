"""Fixtures for mocking of encryption-related functions."""
from unittest.mock import Mock

from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.transport.message_service import _MessageEncryption

_sign_sentinel: bytes = b"i_am_not_a_real_signature"


@fixture
def mock_rsa_encryption(mocker: MockerFixture) -> Mock:
    """Mock out RSAEncryption.encrypt().

    Simply returns the message passed in.

    Should be used in conjunction with the mock_rsa_decryption fixture if both
    encryption and decryption are needed.
    """
    mock_rsa_encryption: Mock = mocker.patch.object(
        _RSAEncryption,
        "encrypt",
        autospec=True,
        side_effect=lambda message, _key: message,
    )
    return mock_rsa_encryption


@fixture
def mock_rsa_decryption(mocker: MockerFixture) -> Mock:
    """Mock out RSAEncryption.decrypt().

    Simply returns the ciphertext passed in.

    Should be used in conjunction with the mock_rsa_encryption fixture if both
    encryption and decryption are needed.
    """
    mock_rsa_decryption: Mock = mocker.patch.object(
        _RSAEncryption,
        "decrypt",
        autospec=True,
        side_effect=lambda ciphertext, _key: ciphertext,
    )
    return mock_rsa_decryption


@fixture
def mock_rsa_sign_message(mocker: MockerFixture) -> Mock:
    """Mock out RSAEncryption.sign_message().

    Simply returns a sentinel signature.

    Should be used in conjunction with the mock_rsa_signature_verification fixture
    if both signing and validating are needed.
    """
    mock_rsa_sign_message: Mock = mocker.patch.object(
        _RSAEncryption,
        "sign_message",
        autospec=True,
        side_effect=lambda _key, _message: _sign_sentinel,
    )
    return mock_rsa_sign_message


@fixture
def mock_rsa_signature_verification(mocker: MockerFixture) -> Mock:
    """Mock out RSAEncryption.verify_signature().

    Returns True if the signature is the sentinel signature, False otherwise.

    Should be used in conjunction with the mock_rsa_sign_message fixture if both
    signing and validating are needed.
    """
    mock_rsa_signature_verification: Mock = mocker.patch.object(
        _RSAEncryption,
        "verify_signature",
        autospec=True,
        side_effect=lambda _key, signature, _message: bool(signature == _sign_sentinel),
    )
    return mock_rsa_signature_verification


@fixture
def mock_message_aes_encryption(mocker: MockerFixture) -> Mock:
    """Mock out MessageEncryption.encrypt_outgoing_message().

    Simply returns the message body passed in.

    Should be used in conjunction with the mock_message_aes_decryption fixture if both
    encryption and decryption are needed.
    """
    mock_message_aes_encryption: Mock = mocker.patch.object(
        _MessageEncryption,
        "encrypt_outgoing_message",
        autospec=True,
        side_effect=lambda body, _key: body,
    )
    return mock_message_aes_encryption


@fixture
def mock_message_aes_decryption(mocker: MockerFixture) -> Mock:
    """Mock out MessageEncryption.decrypt_incoming_message().

    Simply returns the message body passed in.

    Should be used in conjunction with the mock_message_aes_encryption fixture if both
    encryption and decryption are needed.
    """
    mock_message_aes_decryption: Mock = mocker.patch.object(
        _MessageEncryption,
        "decrypt_incoming_message",
        autospec=True,
        side_effect=lambda body, _key: body,
    )
    return mock_message_aes_decryption
