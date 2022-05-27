"""Test Authorisation Checkers."""
import asyncio
from datetime import datetime, timedelta, timezone
import functools
import logging
import re
from types import MethodType
from typing import Callable, Dict, List, Literal, Optional, Type, Union, cast
from unittest.mock import AsyncMock, Mock, NonCallableMock, call, create_autospec

from _pytest.logging import LogCaptureFixture
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from requests import HTTPError, RequestException
import responses

from bitfount import web_utils
from bitfount.federated.authorisation_checkers import (
    IdentityVerificationMethod,
    _LocalAuthorisation,
    _OIDCAuthorisationCode,
    _OIDCDeviceCode,
    _SAMLAuthorisation,
    _SignatureBasedAuthorisation,
    check_identity_verification_method,
)
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.task_requests import (
    _EncryptedTaskRequest,
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.types import (
    _OIDCAuthFlowResponse,
    _PodDeviceCodeDetails,
)
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import (
    SerializedAlgorithm,
    SerializedProtocol,
    _PodResponseType,
    _TaskRequestMessageGenerator,
)
from bitfount.hub.api import BitfountAM, BitfountHub
from bitfount.hub.authentication_flow import (
    _AUTHORIZATION_PENDING_ERROR,
    _DEVICE_CODE_GRANT_TYPE,
    _SLOW_DOWN_ERROR,
    _AuthEnv,
)
from bitfount.hub.types import (
    _DeviceAccessTokenRequestDict,
    _DeviceAccessTokenResponseJSON,
    _PKCEAccessTokenResponseJSON,
)
from tests.utils import PytestRequest
from tests.utils.helper import get_info_logs, get_warning_logs, unit_test


@unit_test
class TestIdentityVerificationMethodChecker:
    """Tests for check_identity_verification_method()."""

    def test_check_identity_verification_method_passes_for_listed_methods(self) -> None:
        """Check function passes for expected values (str or enum)."""
        # Test works with string-based values
        for method in IdentityVerificationMethod:
            assert check_identity_verification_method(method.value) == method

        # Test works with enum-based values
        for method in IdentityVerificationMethod:
            assert check_identity_verification_method(method) == method

    def test_check_identity_verification_method_raises_exception_on_unrecognised(
        self,
    ) -> None:
        """Check function raises exception when passed unrecognised method."""
        fake_method = "fake_method"
        with pytest.raises(
            ValueError, match=f"Unsupported identity verification method: {fake_method}"
        ):
            check_identity_verification_method(fake_method)


@fixture
def pod_identifier() -> str:
    """Single pod identifier."""
    return "someUser/somePod"


@fixture
def pod_identifiers() -> List[str]:
    """List of pod identifiers."""
    return ["pod_1/identifier_1", "pod_1/identifier_2"]


@fixture
def serialized_protocol() -> SerializedProtocol:
    """Protocol details."""
    return SerializedProtocol(
        class_name="some protocol",
        algorithm=SerializedAlgorithm(class_name="some algorithm"),
    )


@fixture
def modeller_name() -> str:
    """Name of modeller."""
    return "someModeller"


@fixture(params=[True, False], ids=lambda arg: f"serialize_input={arg}")
def serialize_as_bytes(request: PytestRequest) -> bool:
    """Determines whether the method input should be serialized or not."""
    return cast(bool, request.param)


@fixture
def aes_key() -> bytes:
    """Fake AES key."""
    return b"an_aes_key"


@fixture
def mock_pod_public_key() -> NonCallableMock:
    """Mock pod RSA public key."""
    mock_pod_public_key: NonCallableMock = create_autospec(RSAPublicKey, instance=True)
    return mock_pod_public_key


@fixture
def mock_pod_private_key() -> NonCallableMock:
    """Mock pod RSA private key."""
    mock_pod_private_key: NonCallableMock = create_autospec(
        RSAPrivateKey, instance=True
    )
    return mock_pod_private_key


@fixture
def mock_task_request() -> NonCallableMock:
    """Mock TaskRequest instance.

    serialize() returns a static value.
    """
    mock_task_request: NonCallableMock = create_autospec(_TaskRequest, instance=True)
    mock_task_request.serialize.return_value = b"mock_task_request"
    return mock_task_request


@fixture
def mock_task_request_import(
    mock_task_request: NonCallableMock, mocker: MockerFixture
) -> Mock:
    """Mocks the TaskRequest import in authorisation_checkers.py.

    Constructor and deserialize method will return the mock instance defined.
    """
    mock_task_request_import: Mock = mocker.patch(
        "bitfount.federated.authorisation_checkers._TaskRequest",
        return_value=mock_task_request,
    )
    mock_task_request_import.deserialize.return_value = mock_task_request
    return mock_task_request_import


@fixture
def mock_encrypted_task_request() -> NonCallableMock:
    """Mock EncryptedTaskRequest instance.

    serialize() returns a static value.
    """
    mock_encrypted_task_request: NonCallableMock = create_autospec(
        _EncryptedTaskRequest, instance=True
    )
    mock_encrypted_task_request.serialize.return_value = b"mock_encrypted_task_request"
    return mock_encrypted_task_request


@fixture
def mock_encrypted_tr_import(
    mock_encrypted_task_request: NonCallableMock, mocker: MockerFixture
) -> Mock:
    """Mocks the EncryptedTaskRequest import in authorisation_checkers.py.

    Constructor and deserialize method will return the mock instance defined.
    """
    mock_encrypted_tr_import: Mock = mocker.patch(
        "bitfount.federated.authorisation_checkers._EncryptedTaskRequest",
        return_value=mock_encrypted_task_request,
    )
    mock_encrypted_tr_import.deserialize.return_value = mock_encrypted_task_request
    return mock_encrypted_tr_import


@fixture
def mock_signed_encrypted_task_request() -> NonCallableMock:
    """Mock SignedEncryptedTaskRequest instance.

    serialize() returns a static value.
    """
    mock_encrypted_task_request: NonCallableMock = create_autospec(
        _SignedEncryptedTaskRequest, instance=True
    )
    mock_encrypted_task_request.serialize.return_value = (
        b"mock_signed_encrypted_task_request"
    )
    return mock_encrypted_task_request


@fixture
def mock_signed_encrypted_tr_import(
    mock_signed_encrypted_task_request: NonCallableMock, mocker: MockerFixture
) -> Mock:
    """Mocks the SignedEncryptedTaskRequest import in authorisation_checkers.py.

    Constructor and deserialize method will return the mock instance defined.
    """
    mock_signed_encrypted_tr_import: Mock = mocker.patch(
        "bitfount.federated.authorisation_checkers._SignedEncryptedTaskRequest",
        return_value=mock_signed_encrypted_task_request,
    )
    mock_signed_encrypted_tr_import.deserialize.return_value = (
        mock_signed_encrypted_task_request
    )
    return mock_signed_encrypted_tr_import


@fixture
def mock_task_request_message() -> NonCallableMock:
    """Mock TaskRequestMessage instance.

    serialize() returns a static value.
    """
    mock_task_request_message: NonCallableMock = create_autospec(
        _TaskRequestMessage, instance=True
    )
    mock_task_request_message.serialize.return_value = b"mock_task_request_message"
    return mock_task_request_message


@fixture
def mock_task_request_message_import(
    mock_task_request_message: NonCallableMock, mocker: MockerFixture
) -> Mock:
    """Mocks the TaskRequestMessage import in authorisation_checkers.py.

    Constructor and deserialize method will return the mock instance defined.
    """
    mock_task_request_message_import: Mock = mocker.patch(
        "bitfount.federated.authorisation_checkers._TaskRequestMessage",
        return_value=mock_task_request_message,
    )
    mock_task_request_message_import.deserialize.return_value = (
        mock_task_request_message
    )
    return mock_task_request_message_import


@fixture
def task_request(
    aes_key: bytes, pod_identifiers: List[str], serialized_protocol: SerializedProtocol
) -> _TaskRequest:
    """Constructed TaskRequest instance."""
    return _TaskRequest(serialized_protocol, pod_identifiers, aes_key)


@fixture
def encrypted_task_request(task_request: _TaskRequest) -> _EncryptedTaskRequest:
    """Constructed EncryptedTaskRequest instance.

    The `encrypted_request` parameter is not actually encrypted, but just serialized
    to bytes.
    """
    # Not encrypted contents
    return _EncryptedTaskRequest(encrypted_request=task_request.serialize())


@fixture
def signed_encrypted_task_request(
    task_request: _TaskRequest,
) -> _SignedEncryptedTaskRequest:
    """Constructed SignedEncryptedTaskRequest instance.

    The `encrypted_request` parameter is not actually encrypted, but just serialized
    to bytes. The signature is a static value.
    """
    # Not encrypted contents, fake signature
    return _SignedEncryptedTaskRequest(
        encrypted_request=task_request.serialize(), signature=b"fake_signature"
    )


@fixture
def get_task_request_message(
    encrypted_task_request: _EncryptedTaskRequest,
    serialized_protocol: SerializedProtocol,
) -> Callable[[str], _TaskRequestMessage]:
    """Return function that will create TaskRequestMessage instances from auth_type."""

    def _make_task_request_message(auth_type: str) -> _TaskRequestMessage:
        return _TaskRequestMessage(
            serialized_protocol=serialized_protocol,
            auth_type=auth_type,
            request=encrypted_task_request.serialize(),
        )

    return _make_task_request_message


@fixture
def get_signed_task_request_message(
    serialized_protocol: SerializedProtocol,
    signed_encrypted_task_request: _EncryptedTaskRequest,
) -> Callable[[str], _TaskRequestMessage]:
    """Return function that will create TaskRequestMessage instances from auth_type.

    Inner message type is a signed and encrypted task request.
    """

    def _make_task_request_message(auth_type: str) -> _TaskRequestMessage:
        return _TaskRequestMessage(
            serialized_protocol=serialized_protocol,
            auth_type=auth_type,
            request=signed_encrypted_task_request.serialize(),
        )

    return _make_task_request_message


@unit_test
class TestLocalAuthorisation:
    """Tests Local Authorisation."""

    async def test_local_authorisation_approves(
        self,
        modeller_name: str,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Tests local authorisation.

        This authoriser 'approves' all requests for local use
        it simply returns the PodResponseMessage given to it.
        """
        expected_pod_response = _PodResponseMessage(modeller_name, pod_identifier)
        authoriser = _LocalAuthorisation(expected_pod_response, serialized_protocol)

        result = await authoriser.check_authorisation()

        assert result == expected_pod_response
        assert result.messages == {}

    def test__generate_task_request_message(
        self,
        aes_key: bytes,
        mock_encrypted_task_request: NonCallableMock,
        mock_encrypted_tr_import: Mock,
        mock_pod_public_key: NonCallableMock,
        mock_rsa_encryption: Mock,
        mock_task_request: NonCallableMock,
        mock_task_request_import: Mock,
        mock_task_request_message: NonCallableMock,
        mock_task_request_message_import: Mock,
        pod_identifiers: List[str],
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Tests the _generate_task_request_message method for Local Authorisation."""
        trm = _LocalAuthorisation._generate_task_request_message(
            serialized_protocol=serialized_protocol,
            pod_identifiers=pod_identifiers,
            aes_key=aes_key,
            pod_public_key=mock_pod_public_key,
        )

        # Check TaskRequest constructed as expected
        mock_task_request_import.assert_called_once_with(
            serialized_protocol, pod_identifiers, aes_key
        )
        # Check EncryptedTaskRequest constructed as expected (mocked RSA encryption
        # means serialize return value will be passed)
        mock_encrypted_tr_import.assert_called_once_with(
            mock_task_request.serialize.return_value
        )
        # Check encryption done
        mock_rsa_encryption.assert_called_once_with(
            mock_task_request.serialize.return_value,
            mock_pod_public_key,
        )
        # Check TaskRequestMessage constructed as expected
        mock_task_request_message_import.assert_called_once_with(
            serialized_protocol,
            IdentityVerificationMethod.LOCAL.value,
            mock_encrypted_task_request.serialize.return_value,
        )
        # Check that output value is serialized TaskRequestMessage
        assert trm == mock_task_request_message.serialize.return_value

    def test_extract_from_task_request_message(
        self,
        encrypted_task_request: _EncryptedTaskRequest,
        get_task_request_message: Callable[[str], _TaskRequestMessage],
        serialize_as_bytes: bool,
    ) -> None:
        """Tests extract_from_task_request_message for Local Authorisation.

        Tests for both deserialized and serialized inputs.
        """
        task_request_message = get_task_request_message(
            IdentityVerificationMethod.LOCAL.value
        )

        if serialize_as_bytes:
            extracted = _LocalAuthorisation.extract_from_task_request_message(
                task_request_message.serialize()
            )
        else:
            extracted = _LocalAuthorisation.extract_from_task_request_message(
                task_request_message
            )

        assert extracted == encrypted_task_request

    def test_create_task_request_message_generator(self) -> None:
        """Checks create_task_request_message_generator returns right type."""
        assert isinstance(
            _LocalAuthorisation.create_task_request_message_generator(),
            _TaskRequestMessageGenerator,
        )

    def test_unpack_task_request(
        self,
        get_task_request_message: Callable[[str], _TaskRequestMessage],
        mock_pod_private_key: NonCallableMock,
        mock_rsa_decryption: Mock,
        serialize_as_bytes: bool,
        task_request: _TaskRequest,
    ) -> None:
        """Tests unpack_task_request for Local Authorisation.

        Tests for both deserialized and serialized inputs.
        """
        task_request_message = get_task_request_message(
            IdentityVerificationMethod.LOCAL.value
        )

        if serialize_as_bytes:
            unpacked = _LocalAuthorisation.unpack_task_request(
                task_request_message.serialize(), mock_pod_private_key
            )
        else:
            unpacked = _LocalAuthorisation.unpack_task_request(
                task_request_message, mock_pod_private_key
            )

        assert unpacked == task_request


@unit_test
class TestSignatureBasedAuthorisation:
    """Tests Signature (Private Key) Authorisation Checker."""

    @fixture
    def mock_hub(self) -> Mock:
        """Mock hub."""
        hub: Mock = create_autospec(BitfountHub, instance=True)
        return hub

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    @pytest.mark.parametrize(
        "response_type,expected_messages",
        [
            (_PodResponseType.ACCEPT, {}),
            (
                _PodResponseType.ACCESS_MANAGER_NOT_AUTHORISED,
                {_PodResponseType.ACCESS_MANAGER_NOT_AUTHORISED.name: []},
            ),
        ],
    )
    async def test_signature_authorisation_returns_responses(
        self,
        expected_messages: Dict[str, str],
        modeller_name: str,
        pod_identifier: str,
        response_type: _PodResponseType,
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Test Signature Authorisation returns expected PodResponseMessages."""
        encrypted_task = b"some task"
        signature = b"some signature"

        authoriser = _SignatureBasedAuthorisation(
            pod_response_message=_PodResponseMessage(modeller_name, pod_identifier),
            encrypted_task_request=encrypted_task,
            signature=signature,
            serialized_protocol=serialized_protocol,
        )

        result = await authoriser.check_authorisation()

        assert result.messages == expected_messages

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    def test__generate_task_request_message(
        self,
        aes_key: bytes,
        mock_pod_private_key: NonCallableMock,
        mock_pod_public_key: NonCallableMock,
        mock_rsa_encryption: Mock,
        mock_rsa_sign_message: Mock,
        mock_signed_encrypted_task_request: NonCallableMock,
        mock_signed_encrypted_tr_import: Mock,
        mock_task_request: NonCallableMock,
        mock_task_request_import: Mock,
        mock_task_request_message: NonCallableMock,
        mock_task_request_message_import: Mock,
        pod_identifiers: List[str],
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Test the generate_task_request_message method in sig-based authorisation."""
        # Create inner message maker class
        message_maker = _SignatureBasedAuthorisation._SignedMessageMaker(
            mock_pod_private_key
        )

        # Call
        trm = message_maker.generate_task_request_message(
            serialized_protocol=serialized_protocol,
            pod_identifiers=pod_identifiers,
            aes_key=aes_key,
            pod_public_key=mock_pod_public_key,
        )

        # Check TaskRequest constructed as expected
        mock_task_request_import.assert_called_once_with(
            serialized_protocol, pod_identifiers, aes_key
        )
        # Check encryption done
        mock_rsa_encryption.assert_called_once_with(
            mock_task_request.serialize.return_value,
            mock_pod_public_key,
        )
        # Check signing done (mocked RSA encryption means serialize() return value
        # will be passed)
        mock_rsa_sign_message.assert_called_once_with(
            mock_pod_private_key, mock_task_request.serialize.return_value
        )
        # Check SignedEncryptedTaskRequest constructed as expected (mocked RSA
        # encryption means serialize() return value will be passed; mocked signing
        # means static value passed)
        mock_signed_encrypted_tr_import.assert_called_once_with(
            mock_task_request.serialize.return_value,
            mock_rsa_sign_message(None, None),  # extract signature value
        )
        # Check TaskRequestMessage constructed as expected
        mock_task_request_message_import.assert_called_once_with(
            serialized_protocol,
            IdentityVerificationMethod.KEYS.value,  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
            mock_signed_encrypted_task_request.serialize.return_value,
        )
        # Check that output value is serialized TaskRequestMessage
        assert trm == mock_task_request_message.serialize.return_value

    def test_create_task_request_message_generator(
        self,
        mock_pod_private_key: NonCallableMock,
    ) -> None:
        """Test _SignatureBasedAuthorisation.create_task_request_message_generator()."""
        message_generator = (
            _SignatureBasedAuthorisation.create_task_request_message_generator(
                mock_pod_private_key
            )
        )

        # Check right type
        assert isinstance(message_generator, _TaskRequestMessageGenerator)
        # Check key matches in created inner class
        wrapper_class = cast(MethodType, message_generator).__self__
        assert isinstance(
            wrapper_class, _SignatureBasedAuthorisation._SignedMessageMaker
        )
        assert wrapper_class.private_key == mock_pod_private_key

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    def test_extract_from_task_request_message(
        self,
        get_signed_task_request_message: Callable[[str], _TaskRequestMessage],
        serialize_as_bytes: bool,
        signed_encrypted_task_request: _SignedEncryptedTaskRequest,
    ) -> None:
        """Test _SignatureBasedAuthorisation.extract_from_task_request_message().

        Tests for both deserialized and serialized inputs.
        """
        task_request_message = get_signed_task_request_message(
            IdentityVerificationMethod.KEYS.value  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
        )

        if serialize_as_bytes:
            extracted = _SignatureBasedAuthorisation.extract_from_task_request_message(
                task_request_message.serialize()
            )
        else:
            extracted = _SignatureBasedAuthorisation.extract_from_task_request_message(
                task_request_message
            )

        assert extracted == signed_encrypted_task_request

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    def test_unpack_task_request(
        self,
        get_signed_task_request_message: Callable[[str], _TaskRequestMessage],
        mock_pod_private_key: NonCallableMock,
        mock_rsa_decryption: Mock,
        serialize_as_bytes: bool,
        task_request: _TaskRequest,
    ) -> None:
        """Test _SignatureBasedAuthorisation.unpack_task_request().

        Tests for both deserialized and serialized inputs.
        """
        task_request_message = get_signed_task_request_message(
            IdentityVerificationMethod.KEYS.value  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
        )

        if serialize_as_bytes:
            unpacked = _SignatureBasedAuthorisation.unpack_task_request(
                task_request_message.serialize(), mock_pod_private_key
            )
        else:
            unpacked = _SignatureBasedAuthorisation.unpack_task_request(
                task_request_message, mock_pod_private_key
            )

        assert unpacked == task_request


@unit_test
class TestSAMLAuthorisation:
    """Tests SAML Authorisation Checker."""

    @fixture
    def pod_name(self) -> str:
        """Pod name."""
        return "somePod"

    @fixture
    def saml_request(self) -> str:
        """SAML Request."""
        return "some saml request"

    @fixture
    def saml_id(self) -> str:
        """SAML Request ID."""
        return "some saml ID"

    @fixture
    def saml_response(self) -> str:
        """SAML Response."""
        return "some saml response"

    @fixture
    def access_manager(self, saml_id: str, saml_request: str) -> Mock:
        """Mock access manager."""
        access_manager: Mock = create_autospec(BitfountAM, instance=True)
        access_manager.get_saml_challenge.return_value = saml_request, saml_id
        return access_manager

    @fixture
    def worker_mailbox(
        self, modeller_name: str, pod_identifier: str, saml_response: str
    ) -> Mock:
        """Mock worker mailbox."""
        mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
        mailbox.get_saml_response = AsyncMock(return_value=saml_response)
        mailbox.modeller_name = modeller_name
        mailbox.pod_identifier = pod_identifier
        return mailbox

    @pytest.mark.parametrize(
        "response_type,expected_messages",
        [
            (_PodResponseType.ACCEPT, {}),
            (
                _PodResponseType.ACCESS_MANAGER_NOT_AUTHORISED,
                {_PodResponseType.ACCESS_MANAGER_NOT_AUTHORISED.name: []},
            ),
        ],
    )
    async def test_saml_authorisation_returns_responses(
        self,
        access_manager: Mock,
        expected_messages: Dict[str, List[str]],
        modeller_name: str,
        pod_identifier: str,
        pod_name: str,
        response_type: _PodResponseType,
        saml_id: str,
        saml_request: str,
        saml_response: str,
        serialized_protocol: SerializedProtocol,
        worker_mailbox: Mock,
    ) -> None:
        """Test SAML Authorisation returns expected PodResponseMessages."""
        access_manager.validate_saml_response.return_value = response_type
        response_message = _PodResponseMessage(modeller_name, pod_identifier)
        authoriser = _SAMLAuthorisation(
            pod_response_message=response_message,
            access_manager=access_manager,
            mailbox=worker_mailbox,
            serialized_protocol=serialized_protocol,
        )

        result = await authoriser.check_authorisation()

        worker_mailbox.issue_saml_challenge.assert_called_once_with(saml_request)
        access_manager.validate_saml_response.assert_called_once_with(
            saml_response, saml_id, pod_identifier, modeller_name, serialized_protocol
        )

        assert result.messages == expected_messages

    def test_extract_from_task_request_message(
        self,
        encrypted_task_request: _EncryptedTaskRequest,
        get_task_request_message: Callable[[str], _TaskRequestMessage],
        serialize_as_bytes: bool,
    ) -> None:
        """Tests extract_from_task_request_message for SAML Authorisation.

        Tests for both deserialized and serialized inputs.
        """
        task_request_message = get_task_request_message(
            IdentityVerificationMethod.SAML.value
        )

        if serialize_as_bytes:
            extracted = _SAMLAuthorisation.extract_from_task_request_message(
                task_request_message.serialize()
            )
        else:
            extracted = _SAMLAuthorisation.extract_from_task_request_message(
                task_request_message
            )

        assert extracted == encrypted_task_request


@fixture
def mock_access_manager() -> Mock:
    """Mock access manager."""
    access_manager: Mock = create_autospec(BitfountAM, instance=True)
    return access_manager


@fixture
def mock_worker_mailbox(modeller_name: str, pod_identifier: str) -> Mock:
    """Mock worker mailbox."""
    mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
    mailbox.modeller_name = modeller_name
    mailbox.pod_identifier = pod_identifier
    return mailbox


@fixture
def fake_auth_domain() -> str:
    """A fake auth domain for tests."""
    return "fake_auth_domain"


@fixture
def fake_client_id() -> str:
    """A fake client ID for tests."""
    return "fake_client_id"


@unit_test
class TestOIDCAuthCodeAuthorisation:
    """Tests for _OIDCAuthorisationCode authoriser."""

    @fixture
    def auth_code(self) -> str:
        """Auth code for tests."""
        return "auth_code_for_tests"

    @fixture
    def code_verifier(self) -> str:
        """Code verifier for tests."""
        return "code_verifier_for_tests"

    @fixture
    def redirect_uri(self) -> str:
        """Redirect URI for tests."""
        return "redirect_uri"

    @fixture
    def pkce_access_token_response_json(self) -> _PKCEAccessTokenResponseJSON:
        """Response JSON from /oauth/token."""
        response_json: _PKCEAccessTokenResponseJSON = {
            "access_token": "access_token_value",
            "refresh_token": "refresh_token_value",
            "id_token": "id_token_value",
            "token_type": "Bearer",
            "expires_in": 60 * 60,
        }
        return response_json

    @fixture
    def oidc_auth_code_authoriser(
        self,
        fake_auth_domain: str,
        fake_client_id: str,
        mock_access_manager: Mock,
        mock_worker_mailbox: Mock,
        modeller_name: str,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
    ) -> _OIDCAuthorisationCode:
        """Constructed OIDC authoriser for tests."""
        pod_response_message = _PodResponseMessage(modeller_name, pod_identifier)
        return _OIDCAuthorisationCode(
            pod_response_message=pod_response_message,
            access_manager=mock_access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=serialized_protocol,
            _auth_domain=fake_auth_domain,
            _client_id=fake_client_id,
        )

    def test__generate_task_request_message(
        self,
        aes_key: bytes,
        mock_encrypted_task_request: NonCallableMock,
        mock_encrypted_tr_import: Mock,
        mock_pod_public_key: NonCallableMock,
        mock_rsa_encryption: Mock,
        mock_task_request: NonCallableMock,
        mock_task_request_import: Mock,
        mock_task_request_message: NonCallableMock,
        mock_task_request_message_import: Mock,
        pod_identifiers: List[str],
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Test _generate_task_request_message for OIDC Authorisation."""
        trm = _OIDCAuthorisationCode._generate_task_request_message(
            serialized_protocol=serialized_protocol,
            pod_identifiers=pod_identifiers,
            aes_key=aes_key,
            pod_public_key=mock_pod_public_key,
        )

        # Check TaskRequest constructed as expected
        mock_task_request_import.assert_called_once_with(
            serialized_protocol, pod_identifiers, aes_key
        )
        # Check EncryptedTaskRequest constructed as expected (mocked RSA encryption
        # means serialize return value will be passed)
        mock_encrypted_tr_import.assert_called_once_with(
            mock_task_request.serialize.return_value
        )
        # Check encryption done
        mock_rsa_encryption.assert_called_once_with(
            mock_task_request.serialize.return_value,
            mock_pod_public_key,
        )
        # Check TaskRequestMessage constructed as expected
        mock_task_request_message_import.assert_called_once_with(
            serialized_protocol,
            IdentityVerificationMethod.OIDC_ACF_PKCE.value,
            mock_encrypted_task_request.serialize.return_value,
        )
        # Check that output value is serialized TaskRequestMessage
        assert trm == mock_task_request_message.serialize.return_value

    def test_create_task_request_message_generator(self) -> None:
        """Tests return of OIDC create_task_request_message_generator()."""
        assert isinstance(
            _OIDCAuthorisationCode.create_task_request_message_generator(),
            _TaskRequestMessageGenerator,
        )

    def test__get_client_id(
        self, fake_client_id: str, oidc_auth_code_authoriser: _OIDCAuthorisationCode
    ) -> None:
        """Tests client ID retrieval."""
        # Currently, we expect this to return a static value
        assert oidc_auth_code_authoriser._get_client_id() == fake_client_id

    @responses.activate
    def test__get_access_token(
        self,
        auth_code: str,
        code_verifier: str,
        oidc_auth_code_authoriser: _OIDCAuthorisationCode,
        pkce_access_token_response_json: _PKCEAccessTokenResponseJSON,
        redirect_uri: str,
    ) -> None:
        """Test the _get_access_token POST request and return value."""
        responses.add(
            method=responses.POST,
            url=oidc_auth_code_authoriser._token_endpoint,
            json=pkce_access_token_response_json,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "authorization_code",
                        "client_id": oidc_auth_code_authoriser._client_id,
                        "code": auth_code,
                        "code_verifier": code_verifier,
                        "redirect_uri": redirect_uri,
                    }
                )
            ],
        )

        received_access_token = oidc_auth_code_authoriser._get_access_token(
            auth_code, code_verifier, redirect_uri
        )

        assert received_access_token == pkce_access_token_response_json["access_token"]

    @responses.activate
    def test__get_access_token_non_200_response(
        self,
        auth_code: str,
        code_verifier: str,
        oidc_auth_code_authoriser: _OIDCAuthorisationCode,
        redirect_uri: str,
    ) -> None:
        """Tests _get_access_token throws error, non-200 response."""
        responses.add(
            method=responses.POST,
            url=oidc_auth_code_authoriser._token_endpoint,
            status=400,
        )

        with pytest.raises(HTTPError):
            oidc_auth_code_authoriser._get_access_token(
                auth_code, code_verifier, redirect_uri
            )

    @pytest.mark.parametrize(
        argnames="check_access_response",
        argvalues=(
            pytest.param(_PodResponseType.ACCEPT, id="accept"),
            pytest.param(_PodResponseType.NO_ACCESS, id="no_access"),
            pytest.param(
                _PodResponseType.INVALID_PROOF_OF_IDENTITY,
                id="invalid_proof_of_identity",
            ),
            pytest.param(_PodResponseType.UNAUTHORISED, id="unauthorised"),
            pytest.param(
                _PodResponseType.NO_PROOF_OF_IDENTITY, id="no_proof_of_identity"
            ),
        ),
    )
    async def test_check_authorisation(
        self,
        auth_code: str,
        caplog: LogCaptureFixture,
        check_access_response: _PodResponseType,
        code_verifier: str,
        fake_client_id: str,
        mock_access_manager: Mock,
        mock_worker_mailbox: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        oidc_auth_code_authoriser: _OIDCAuthorisationCode,
        pkce_access_token_response_json: _PKCEAccessTokenResponseJSON,
        pod_identifier: str,
        redirect_uri: str,
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Test authorisation checking for OIDC flow."""
        # Mock out received values from modeller
        mock_worker_mailbox.get_oidc_auth_flow_response.return_value = (
            _OIDCAuthFlowResponse(
                auth_code,
                code_verifier,
                redirect_uri,
            )
        )

        # Mock out _get_access_token
        mock__get_access_token = mocker.patch.object(
            oidc_auth_code_authoriser,
            "_get_access_token",
            autospec=True,
            return_value=pkce_access_token_response_json["access_token"],
        )

        # Mock out API _check_access call
        mock_access_manager.check_oidc_access_request.return_value = (
            check_access_response
        )

        with caplog.at_level(logging.INFO):
            response_message = await oidc_auth_code_authoriser.check_authorisation()

        # Check correct Client ID sent
        mock_worker_mailbox.send_oidc_client_id.assert_awaited_once_with(fake_client_id)
        # Check _get_access_token called as expected
        mock__get_access_token.assert_called_once_with(
            auth_code, code_verifier, redirect_uri
        )
        # Check API call made correctly
        mock_access_manager.check_oidc_access_request.assert_called_once_with(
            pod_identifier=pod_identifier,
            serialized_protocol=serialized_protocol,
            modeller_name=modeller_name,
            modeller_access_token=pkce_access_token_response_json["access_token"],
        )
        # Check logs
        info_logs = get_info_logs(caplog)
        assert (
            f"OIDC authorisation check complete. "
            f"Will inform modeller: {check_access_response.name}" in info_logs
        )

        # Check return
        expected_pod_response = _PodResponseMessage(modeller_name, pod_identifier)
        expected_pod_response.add(check_access_response)
        assert response_message == expected_pod_response


@unit_test
class TestOIDCDeviceCodeAuthorisation:
    """Tests for _OIDCDeviceCode authoriser."""

    @fixture
    def oidc_device_code_authoriser(
        self,
        fake_auth_domain: str,
        fake_client_id: str,
        mock_access_manager: Mock,
        mock_worker_mailbox: Mock,
        modeller_name: str,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
    ) -> _OIDCDeviceCode:
        """An _OIDCDeviceCode authoriser instance."""
        pod_response_message = _PodResponseMessage(modeller_name, pod_identifier)
        return _OIDCDeviceCode(
            pod_response_message=pod_response_message,
            access_manager=mock_access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=serialized_protocol,
            _auth_domain=fake_auth_domain,
            _client_id=fake_client_id,
        )

    def test_auth_domain_and_client_id_always_set(
        self,
        fake_auth_domain: str,
        fake_client_id: str,
        mock_access_manager: Mock,
        mock_worker_mailbox: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Tests default values used if auth_domain and client_id are not set."""
        # Mock _get_auth_environment() function
        mocker.patch(
            "bitfount.federated.authorisation_checkers._get_auth_environment",
            autospec=True,
            return_value=_AuthEnv(
                name="auth_env_name",
                auth_domain=fake_auth_domain,
                client_id=fake_client_id,
            ),
        )

        # Create _OIDCDeviceCode without providing auth_domain or client_id
        pod_response_message = _PodResponseMessage(modeller_name, pod_identifier)
        oidc_device_code_authoriser = _OIDCDeviceCode(
            pod_response_message=pod_response_message,
            access_manager=mock_access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=serialized_protocol,
        )

        # Check defaults set
        assert oidc_device_code_authoriser._auth_domain == fake_auth_domain
        assert oidc_device_code_authoriser._client_id == fake_client_id

    def test__generate_task_request_message(
        self,
        aes_key: bytes,
        mock_encrypted_task_request: NonCallableMock,
        mock_encrypted_tr_import: Mock,
        mock_pod_public_key: NonCallableMock,
        mock_rsa_encryption: Mock,
        mock_task_request: NonCallableMock,
        mock_task_request_import: Mock,
        mock_task_request_message: NonCallableMock,
        mock_task_request_message_import: Mock,
        pod_identifiers: List[str],
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Test _generate_task_request_message for OIDC Authorisation."""
        trm = _OIDCDeviceCode._generate_task_request_message(
            serialized_protocol=serialized_protocol,
            pod_identifiers=pod_identifiers,
            aes_key=aes_key,
            pod_public_key=mock_pod_public_key,
        )

        # Check TaskRequest constructed as expected
        mock_task_request_import.assert_called_once_with(
            serialized_protocol, pod_identifiers, aes_key
        )
        # Check EncryptedTaskRequest constructed as expected (mocked RSA encryption
        # means serialize return value will be passed)
        mock_encrypted_tr_import.assert_called_once_with(
            mock_task_request.serialize.return_value
        )
        # Check encryption done
        mock_rsa_encryption.assert_called_once_with(
            mock_task_request.serialize.return_value,
            mock_pod_public_key,
        )
        # Check TaskRequestMessage constructed as expected
        mock_task_request_message_import.assert_called_once_with(
            serialized_protocol,
            IdentityVerificationMethod.OIDC_DEVICE_CODE.value,
            mock_encrypted_task_request.serialize.return_value,
        )
        # Check that output value is serialized TaskRequestMessage
        assert trm == mock_task_request_message.serialize.return_value

    def test_create_task_request_message_generator(self) -> None:
        """Tests return of OIDC create_task_request_message_generator()."""
        assert isinstance(
            _OIDCDeviceCode.create_task_request_message_generator(),
            _TaskRequestMessageGenerator,
        )

    @fixture
    def device_code(self) -> str:
        """Device code."""
        return "someDeviceCode"

    @fixture
    def expires_at(self) -> datetime:
        """The code expiration time as a datetime."""
        return datetime.now(timezone.utc) + timedelta(seconds=900)

    @fixture
    def interval(self) -> int:
        """The polling interval to use with the device code."""
        return 5

    @fixture
    def token_endpoint(self, fake_auth_domain: str) -> str:
        """The expected token API endpoint."""
        return f"https://{fake_auth_domain}/oauth/token"

    @fixture
    def token_request(
        self, device_code: str, fake_client_id: str
    ) -> _DeviceAccessTokenRequestDict:
        """Expected request data for /oauth/token."""
        return {
            "client_id": fake_client_id,
            "grant_type": _DEVICE_CODE_GRANT_TYPE,
            "device_code": device_code,
        }

    @fixture
    def access_token(self) -> str:
        """Access token."""
        return "someAccessToken"

    @fixture
    def token_response(self, access_token: str) -> _DeviceAccessTokenResponseJSON:
        """Expected response data from /oauth/token."""
        return {
            "access_token": access_token,
            "id_token": "eyJ...0NE",
            "refresh_token": "eyJ...MoQ",
            "scope": "...",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

    @fixture
    def mock_asyncio_sleep(self, mocker: MockerFixture) -> Mock:
        """Mock out asyncio.sleep() calls."""
        return mocker.patch.object(asyncio, "sleep", autospec=True)

    async def test__poll_for_access_token(
        self,
        access_token: str,
        caplog: LogCaptureFixture,
        device_code: str,
        expires_at: datetime,
        interval: int,
        mock_asyncio_sleep: Mock,
        oidc_device_code_authoriser: _OIDCDeviceCode,
        token_endpoint: str,
        token_request: _DeviceAccessTokenRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Test _poll_for_access_token() works correctly."""
        # We have to use the context manager as decorator doesn't work on async.
        # Can change when: https://github.com/getsentry/responses/pull/478 is released.
        with responses.RequestsMock() as rsps:
            # Add one initial "not ready yet" response
            rsps.add(
                responses.POST,
                token_endpoint,
                status=400,
                json={"error": _AUTHORIZATION_PENDING_ERROR},
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )
            # Then next response is the passing one
            rsps.add(
                responses.POST,
                token_endpoint,
                json=token_response,
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )

            with caplog.at_level(logging.INFO):
                received_access_token = (
                    await oidc_device_code_authoriser._poll_for_access_token(
                        device_code, expires_at, interval
                    )
                )

            # Check received info
            assert received_access_token == access_token

            # Check slept once
            mock_asyncio_sleep.assert_awaited_once_with(interval)
            # Check logged out that still waiting
            info_logs = get_info_logs(caplog)
            assert (
                "Waiting on modeller to approve identity verification request..."
                in info_logs
            )

    async def test__poll_for_access_token_handles_slow_down_responses(
        self,
        access_token: str,
        caplog: LogCaptureFixture,
        device_code: str,
        expires_at: datetime,
        interval: int,
        mock_asyncio_sleep: Mock,
        oidc_device_code_authoriser: _OIDCDeviceCode,
        token_endpoint: str,
        token_request: _DeviceAccessTokenRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Tests _poll_for_access_token() handles slow down responses."""
        # We have to use the context manager as decorator doesn't work on async.
        # Can change when: https://github.com/getsentry/responses/pull/478 is released.
        with responses.RequestsMock() as rsps:
            # Add two initial "slow down" responses
            for _ in range(2):
                rsps.add(
                    responses.POST,
                    token_endpoint,
                    status=400,
                    json={"error": _SLOW_DOWN_ERROR},
                    match=[
                        responses.matchers.urlencoded_params_matcher(
                            cast(Dict[str, str], token_request)
                        )
                    ],
                )
            # Then next response is the passing one
            rsps.add(
                responses.POST,
                token_endpoint,
                json=token_response,
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )

            received_access_token = (
                await oidc_device_code_authoriser._poll_for_access_token(
                    device_code, expires_at, interval
                )
            )

            # Check received info
            assert received_access_token == access_token

            # Check slept for expected times and told user
            mock_asyncio_sleep.assert_has_awaits(
                [call(interval + 1), call(interval + 2)]
            )
            warning_logs = get_warning_logs(caplog)
            assert (
                f"Polling token endpoint too frequently. "
                f"Increasing interval from {interval} to {interval+1}" in warning_logs
            )
            assert (
                f"Polling token endpoint too frequently. "
                f"Increasing interval from {interval+1} to {interval + 2}"
                in warning_logs
            )

    @pytest.mark.parametrize(
        argnames=("content_type", "content_value", "expected_error_msg"),
        argvalues=(
            pytest.param(
                "json",
                {},
                'Success response, but JSON was invalid: "{}"',
                id="bad JSON response",
            ),
            pytest.param(
                "body",
                "not a json response",
                'Success response, but JSON was invalid: "not a json response"',
                id="not JSON response",
            ),
        ),
    )
    async def test__poll_for_access_token_fails_bad_200(
        self,
        content_type: Literal["json", "body"],
        content_value: Union[dict, str],
        device_code: str,
        expected_error_msg: str,
        expires_at: datetime,
        interval: int,
        oidc_device_code_authoriser: _OIDCDeviceCode,
        token_endpoint: str,
        token_request: _DeviceAccessTokenRequestDict,
    ) -> None:
        """Tests _poll_for_access_token() handles malformed 200 responses."""
        # We have to use the context manager as decorator doesn't work on async.
        # Can change when: https://github.com/getsentry/responses/pull/478 is released.
        with responses.RequestsMock() as rsps:
            partial_response_add = functools.partial(
                rsps.add,
                responses.POST,
                token_endpoint,
                status=200,
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )
            if content_type == "json":
                partial_response_add(json=content_value)
            else:
                partial_response_add(body=content_value)

            with pytest.raises(
                RequestException,
                match=re.escape(expected_error_msg),
            ):
                await oidc_device_code_authoriser._poll_for_access_token(
                    device_code, expires_at, interval
                )

    @pytest.mark.parametrize(
        argnames=("content_type", "content_value", "expected_error_msg"),
        argvalues=(
            pytest.param(
                "json",
                {"error": "unexpected error"},
                "Error in OAuth response (400) (unexpected error)",
                id="non retry error",
            ),
            pytest.param(
                "json",
                {
                    "error": "unexpected error",
                    "error_description": "unexpected error description",
                },
                (
                    "Error in OAuth response (400) (unexpected error): "
                    "unexpected error description"
                ),
                id="non retry error with description",
            ),
            pytest.param(
                "body",
                "not a json response",
                '400 response, but JSON was invalid: "not a json response"',
                id="not JSON response",
            ),
        ),
    )
    async def test__poll_for_access_token_fails_bad_400(
        self,
        content_type: Literal["json", "body"],
        content_value: Union[dict, str],
        device_code: str,
        expected_error_msg: str,
        expires_at: datetime,
        interval: int,
        oidc_device_code_authoriser: _OIDCDeviceCode,
        token_endpoint: str,
        token_request: _DeviceAccessTokenRequestDict,
    ) -> None:
        """Tests _poll_for_access_token() handles malformed 400 responses."""
        # We have to use the context manager as decorator doesn't work on async.
        # Can change when: https://github.com/getsentry/responses/pull/478 is released.
        with responses.RequestsMock() as rsps:
            partial_response_add = functools.partial(
                rsps.add,
                responses.POST,
                token_endpoint,
                status=400,
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )
            if content_type == "json":
                partial_response_add(json=content_value)
            else:
                partial_response_add(body=content_value)

            with pytest.raises(
                RequestException,
                match=re.escape(expected_error_msg),
            ):
                await oidc_device_code_authoriser._poll_for_access_token(
                    device_code, expires_at, interval
                )

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=(
            100,
            201,
            300,
            401,
            500,
        ),
    )
    @pytest.mark.parametrize(
        argnames=(
            "content_type",
            "content_value",
            "expected_error_type",
            "expected_error_msg",
        ),
        argvalues=(
            pytest.param(
                "json",
                {},
                HTTPError,
                r'An unexpected error occurred: status code: [0-9]{3}; "{}"',
                id="empty JSON",
            ),
            pytest.param(
                "json",
                {"error": "error name"},
                HTTPError,
                r"Error in OAuth response \([0-9]{3}\) \(error name\)",
                id="error JSON",
            ),
            pytest.param(
                "json",
                {"error": "error name", "error_description": "error description"},
                HTTPError,
                (
                    r"Error in OAuth response \([0-9]{3}\) \(error name\): "
                    r"error description"
                ),
                id="error with description JSON",
            ),
            pytest.param(
                "body",
                "not a json response",
                RequestException,
                r'[0-9]{3} response, but JSON was invalid: "not a json response"',
                id="non-JSON response",
            ),
        ),
    )
    async def test__poll_for_access_token_fails_non_200_non_400(
        self,
        content_type: Literal["json", "body"],
        content_value: Union[dict, str],
        device_code: str,
        expected_error_msg: str,
        expected_error_type: Type[Exception],
        expires_at: datetime,
        interval: int,
        oidc_device_code_authoriser: _OIDCDeviceCode,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
        token_endpoint: str,
        token_request: _DeviceAccessTokenRequestDict,
    ) -> None:
        """Tests _poll_for_access_token() fails if non-200/400 response."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        # We have to use the context manager as decorator doesn't work on async.
        # Can change when: https://github.com/getsentry/responses/pull/478 is released.
        with responses.RequestsMock() as rsps:
            partial_response_add = functools.partial(
                rsps.add,
                responses.POST,
                token_endpoint,
                status=status_code,
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )
            if content_type == "json":
                partial_response_add(json=content_value)
            else:
                partial_response_add(body=content_value)

            with pytest.raises(
                expected_error_type,
                match=expected_error_msg,
            ):
                await oidc_device_code_authoriser._poll_for_access_token(
                    device_code, expires_at, interval
                )

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    async def test__poll_for_access_token_fails_when_expired(
        self,
        device_code: str,
        expires_at: datetime,
        interval: int,
        mocker: MockerFixture,
        oidc_device_code_authoriser: _OIDCDeviceCode,
    ) -> None:
        """Tests _poll_for_access_token() fails when device code expires."""
        # Patch out expiration check
        mocker.patch.object(
            oidc_device_code_authoriser, "_has_not_expired", return_value=False
        )

        with pytest.raises(
            TimeoutError,
            match=re.escape(
                "Device code has expired, unable to retrieve access token."
            ),
        ):
            await oidc_device_code_authoriser._poll_for_access_token(
                device_code, expires_at, interval
            )

    @pytest.mark.parametrize(
        argnames="check_access_response",
        argvalues=(
            pytest.param(_PodResponseType.ACCEPT, id="accept"),
            pytest.param(_PodResponseType.NO_ACCESS, id="no_access"),
            pytest.param(
                _PodResponseType.INVALID_PROOF_OF_IDENTITY,
                id="invalid_proof_of_identity",
            ),
            pytest.param(_PodResponseType.UNAUTHORISED, id="unauthorised"),
            pytest.param(
                _PodResponseType.NO_PROOF_OF_IDENTITY, id="no_proof_of_identity"
            ),
        ),
    )
    async def test_check_authorisation(
        self,
        access_token: str,
        caplog: LogCaptureFixture,
        check_access_response: _PodResponseType,
        device_code: str,
        expires_at: datetime,
        fake_client_id: str,
        interval: int,
        mock_access_manager: Mock,
        mock_worker_mailbox: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        oidc_device_code_authoriser: _OIDCDeviceCode,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
    ) -> None:
        """Tests check_authorisation() works as expected."""
        # Patch out receiving device code details
        mock_worker_mailbox.get_oidc_device_code_response.return_value = (
            _PodDeviceCodeDetails(
                device_code=device_code,
                expires_at=expires_at,
                interval=interval,
            )
        )

        # Patch out polling for access token
        mock_poll_for_access_token = mocker.patch.object(
            oidc_device_code_authoriser,
            "_poll_for_access_token",
            autospec=True,
            return_value=access_token,
        )

        # Mock out API _check_access call
        mock_access_manager.check_oidc_access_request.return_value = (
            check_access_response
        )

        # Call
        with caplog.at_level(logging.INFO):
            response_message = await oidc_device_code_authoriser.check_authorisation()

        # Check polling for access token occurred
        mock_poll_for_access_token.assert_awaited_once_with(
            device_code, expires_at, interval
        )

        # Check API call made correctly
        mock_access_manager.check_oidc_access_request.assert_called_once_with(
            pod_identifier=pod_identifier,
            serialized_protocol=serialized_protocol,
            modeller_name=modeller_name,
            modeller_access_token=access_token,
        )

        # Check logs
        info_logs = get_info_logs(caplog)
        assert (
            f"OIDC authorisation check complete. "
            f"Will inform modeller: {check_access_response.name}" in info_logs
        )

        # Check return
        expected_pod_response = _PodResponseMessage(modeller_name, pod_identifier)
        expected_pod_response.add(check_access_response)
        assert response_message == expected_pod_response
