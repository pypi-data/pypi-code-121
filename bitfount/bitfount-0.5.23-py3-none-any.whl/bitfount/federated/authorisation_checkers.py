"""Authorisation Checkers."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Final, List, Mapping, Protocol, Tuple, Type, TypeVar, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import requests
from requests import HTTPError, RequestException, Response
from requests.exceptions import InvalidJSONError

from bitfount import web_utils
from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.task_requests import (
    _EncryptedTaskRequest,
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import (
    SerializedProtocol,
    _PodResponseType,
    _TaskRequestMessageGenerator,
)
from bitfount.hub.api import BitfountAM
from bitfount.hub.authentication_flow import (
    _AUTHORIZATION_PENDING_ERROR,
    _SLOW_DOWN_ERROR,
    _get_auth_environment,
)
from bitfount.hub.types import (
    _DeviceAccessTokenFailResponseJSON,
    _DeviceAccessTokenRequestDict,
    _DeviceAccessTokenResponseJSON,
    _PKCEAccessTokenRequestDict,
    _PKCEAccessTokenResponseJSON,
)

logger = _get_federated_logger(__name__)

# This forces `requests` to make IPv4 connections
# TODO: [BIT-1443] Remove this once Hub/AM support IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined] # Reason: see above # noqa: B950


class IdentityVerificationMethod(Enum):
    """Allowed types of identity verification."""

    # TODO: [BIT-1291] Re-enable KEYS
    # KEYS = "key-based"
    LOCAL = "local"
    OIDC_ACF_PKCE = "oidc-auth-code"
    OIDC_DEVICE_CODE = "oidc-device-code"
    SAML = "saml"

    DEFAULT = OIDC_DEVICE_CODE


#: Allowed types of identity verification as a tuple of strings
IDENTITY_VERIFICATION_METHODS: Final[Tuple[str, ...]] = tuple(
    i.value for i in IdentityVerificationMethod
)
#: Default identity verification method
DEFAULT_IDENTITY_VERIFICATION_METHOD: Final[
    str
] = IdentityVerificationMethod.DEFAULT.value


def check_identity_verification_method(
    method: Union[str, IdentityVerificationMethod]
) -> IdentityVerificationMethod:
    """Checks that the verification method is supported."""
    try:
        return IdentityVerificationMethod(method)
    except ValueError:
        raise ValueError(f"Unsupported identity verification method: {method}")


_M_co = TypeVar("_M_co", covariant=True)


class _AuthorisationChecker(Protocol[_M_co]):
    """Protocol for checking authorisation.

    This is a simple protocol for checking authorisation. It's used to inform a decision
    on whether a Pod accepts or rejects a job.
    """

    serialized_protocol: SerializedProtocol

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        """Creates a callable that can be used to generate task request messages."""
        ...

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _M_co:
        """Extract the packed task request details from the task request message.

        Args:
            task_request_message: The task request message, either packed as bytes
                or unpacked.

        Returns:
            The packed task request details, in the dataclass relevant for this
            authorisation checker.
        """
        ...

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        """Unpacks/decrypts the task request details from the task request message.

        Args:
            msg: The task request message, either packed as bytes or unpacked.
            pod_private_key: The pod's RSA private key, for decryption.
        """
        ...

    async def check_authorisation(self) -> _PodResponseMessage:
        """Check if the task should be executed or not."""
        ...  # Empty method body (explicit '...')


def _make_encrypted_task_request_message(
    auth_type: IdentityVerificationMethod,
    serialized_protocol: SerializedProtocol,
    pod_identifiers: List[str],
    aes_key: bytes,
    pod_public_key: RSAPublicKey,
) -> bytes:
    """Common function for generating messages with _EncryptedTaskRequest contents."""
    # Create task request
    tr = _TaskRequest(serialized_protocol, pod_identifiers, aes_key)

    # Encrypt and pack in class
    packed_tr = _EncryptedTaskRequest(
        _RSAEncryption.encrypt(tr.serialize(), pod_public_key)
    )

    # Create outer message
    message = _TaskRequestMessage(
        serialized_protocol,
        auth_type.value,
        packed_tr.serialize(),
    )
    return message.serialize()


def _extract_encrypted_task_request(
    task_request_message: Union[bytes, _TaskRequestMessage]
) -> _EncryptedTaskRequest:
    """Extract _EncryptedTaskRequest from _TaskRequestMessage."""
    # Deserialize outer message if provided as bytes
    if isinstance(task_request_message, bytes):
        task_request_message = _TaskRequestMessage.deserialize(task_request_message)

    # Deserialize inner _EncryptedTaskRequest
    packed_task_request = _EncryptedTaskRequest.deserialize(
        task_request_message.request
    )

    return packed_task_request


def _unpack_task_request(
    msg: Union[bytes, _TaskRequestMessage],
    pod_private_key: RSAPrivateKey,
    extract_from_task_request_message: Union[
        Callable[[Union[bytes, _TaskRequestMessage]], _EncryptedTaskRequest],
        Callable[[Union[bytes, _TaskRequestMessage]], _SignedEncryptedTaskRequest],
    ],
) -> _TaskRequest:
    """Function for common behaviour to fully unpack _TaskRequest message.

    Args:
        msg: The _TaskRequestMessage, maybe serialized as bytes.
        pod_private_key: The RSA private key of the pod.
        extract_from_task_request_message:
            Callable that will extract the packed task request from the
            _TaskRequestMessage.

    Returns:
        The unpacked task request.
    """
    if isinstance(msg, bytes):
        msg = _TaskRequestMessage.deserialize(msg)
    packed_task_request = extract_from_task_request_message(msg)
    task_request = _TaskRequest.deserialize(
        _RSAEncryption.decrypt(packed_task_request.encrypted_request, pod_private_key)
    )
    return task_request


@dataclass
class _LocalAuthorisation(_AuthorisationChecker[_EncryptedTaskRequest]):
    """Local Authorisation - Accepts anything.

    When running all pods locally, we can assume you're happy
    and that anything you're trying to run is accepted.

    NB: this is currently not used in production.
    """

    pod_response_message: _PodResponseMessage
    serialized_protocol: SerializedProtocol

    @classmethod
    def _generate_task_request_message(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: List[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
    ) -> bytes:
        return _make_encrypted_task_request_message(
            IdentityVerificationMethod.LOCAL,
            serialized_protocol,
            pod_identifiers,
            aes_key,
            pod_public_key,
        )

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _EncryptedTaskRequest:
        return _extract_encrypted_task_request(task_request_message)

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        return cls._generate_task_request_message

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    async def check_authorisation(self) -> _PodResponseMessage:
        """Always returns an accept message."""
        return self.pod_response_message


@dataclass
class _SignatureBasedAuthorisation(_AuthorisationChecker[_SignedEncryptedTaskRequest]):
    """Task authorisation using Signatures.

    Checks whether the Modeller provided signature of the task
    can be verified against the modeller's public key.

    Currently, this is not incorporated into the access manager.
    The signature verification takes places in the pod.
    In the future we will likely move this verification to the access manager,
    so this will become a simpler HTTP call.
    """

    pod_response_message: _PodResponseMessage
    encrypted_task_request: bytes
    signature: bytes
    serialized_protocol: SerializedProtocol

    @dataclass
    class _SignedMessageMaker:
        private_key: RSAPrivateKey

        def generate_task_request_message(
            self,
            serialized_protocol: SerializedProtocol,
            pod_identifiers: List[str],
            aes_key: bytes,
            pod_public_key: RSAPublicKey,
        ) -> bytes:
            tr = _TaskRequest(serialized_protocol, pod_identifiers, aes_key)

            encrypted_tr = _RSAEncryption.encrypt(tr.serialize(), pod_public_key)
            signature = _RSAEncryption.sign_message(self.private_key, encrypted_tr)
            packed_tr = _SignedEncryptedTaskRequest(encrypted_tr, signature)

            message = _TaskRequestMessage(
                serialized_protocol,
                IdentityVerificationMethod.KEYS.value,  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
                packed_tr.serialize(),
            )
            return message.serialize()

    # This is an intentional LSP violation as this class is (currently) the only
    # one with a special create_task_request_message_generator method. As the base
    # class is a Protocol, it cannot be instantiated (so an end-user won't
    # accidentally end up with a different create_task_request_message_generator
    # signature) and for the cases where we need to call this version of the method
    # we can assuage static typing with an isinstance or cast against this class.
    #
    # If more classes appear with different create_task_request_message_generator
    # signatures then we should split the signatures out into their own protocols.
    @classmethod
    def create_task_request_message_generator(  # type: ignore[override] # Reason: see comment # noqa: B950
        cls,
        modeller_private_key: RSAPrivateKey,
    ) -> _TaskRequestMessageGenerator:
        return cls._SignedMessageMaker(
            modeller_private_key
        ).generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _SignedEncryptedTaskRequest:
        if isinstance(task_request_message, bytes):
            task_request_message = _TaskRequestMessage.deserialize(task_request_message)
        packed_task_request = _SignedEncryptedTaskRequest.deserialize(
            task_request_message.request
        )
        return packed_task_request

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    def _check_access(self) -> _PodResponseType:
        """Check that access is allowed for the authorised user and request."""
        # TODO: [BIT-1291] Implement this method once signature-based access is
        #       implemented in Access Manager.
        raise NotImplementedError

    async def check_authorisation(self) -> _PodResponseMessage:
        """Check signature matches modeller public key."""
        self.pod_response_message.add(self._check_access())
        return self.pod_response_message


@dataclass
class _SAMLAuthorisation(_AuthorisationChecker[_EncryptedTaskRequest]):
    """SAML Flow for authorisation.

    This performs a SAML flow,
    sending a SAML challenge and awaiting a response
    then verifying the response with the access manager
    the task is also sent to the access manager to ensure
    that the permissions match up as well.
    """

    pod_response_message: _PodResponseMessage
    access_manager: BitfountAM
    mailbox: _WorkerMailbox
    serialized_protocol: SerializedProtocol

    @classmethod
    def _generate_task_request_message(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: List[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
    ) -> bytes:
        return _make_encrypted_task_request_message(
            IdentityVerificationMethod.SAML,
            serialized_protocol,
            pod_identifiers,
            aes_key,
            pod_public_key,
        )

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        return cls._generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _EncryptedTaskRequest:
        return _extract_encrypted_task_request(task_request_message)

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    async def check_authorisation(self) -> _PodResponseMessage:
        """Perform SAML dance.

        This obtains a SAML challenge from the Access Manager,
        forwards it on to the modeller,
        awaits their SAML response (which comes from their IDP)
        and then sends the SAML response to the Access Manager
        so that the identity can be verified as well as checking
        that the Task sent by the modeller is authorised.
        """
        # We keep the SAML Request ID on behalf of the access manager
        # This allows the access manager some confidence that the SAML
        # response isn't unprompted, as only this pod, on this specific
        # task mailbox can handle the outstanding SAML challenge
        # The Access Manager will verify that the request ID in the
        # response from the modeller matches this request ID which never
        # leaves the pod.
        saml_request, saml_request_id = self.access_manager.get_saml_challenge()

        await self.mailbox.issue_saml_challenge(saml_request)

        saml_response = await self.mailbox.get_saml_response()

        # Check with Access Manager that user matches expected identity
        # and that the user has the correct permissions for the task
        # that they have requested.
        authentication_result: _PodResponseType = (
            self.access_manager.validate_saml_response(
                saml_response,
                saml_request_id,
                self.pod_response_message.pod_identifier,
                self.mailbox.modeller_name,
                self.serialized_protocol,
            )
        )
        logger.info(
            f"SAML Exchange complete. "
            f"Will inform modeller: {authentication_result.name}"
        )
        self.pod_response_message.add(authentication_result)
        return self.pod_response_message


@dataclass
class _OIDCAuthorisationCode(_AuthorisationChecker[_EncryptedTaskRequest]):
    """OIDC Authorisation Code Flow with PKCE.

    See: https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce  # noqa: B950
    """

    pod_response_message: _PodResponseMessage
    access_manager: BitfountAM
    mailbox: _WorkerMailbox
    serialized_protocol: SerializedProtocol

    # Auth-related params
    _auth_domain: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: B950
    _client_id: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: B950

    def __post_init__(self) -> None:
        # Fill auth-related attributes if not provided
        auth_env = _get_auth_environment()
        if not self._auth_domain:
            self._auth_domain = auth_env.auth_domain
        if not self._client_id:
            self._client_id = auth_env.client_id

        self._token_endpoint: str = f"https://{self._auth_domain}/oauth/token"

    @classmethod
    def _generate_task_request_message(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: List[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
    ) -> bytes:
        return _make_encrypted_task_request_message(
            IdentityVerificationMethod.OIDC_ACF_PKCE,
            serialized_protocol,
            pod_identifiers,
            aes_key,
            pod_public_key,
        )

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        return cls._generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _EncryptedTaskRequest:
        return _extract_encrypted_task_request(task_request_message)

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    async def check_authorisation(self) -> _PodResponseMessage:
        """Perform OIDC flow from the pod-side.

        This flow is based on:
        https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce  # noqa: B950
        """
        # Retrieve client ID for pod and send to modeller
        client_id = self._get_client_id()
        await self.mailbox.send_oidc_client_id(client_id)

        # Wait for authorization code and code verifier
        response = await self.mailbox.get_oidc_auth_flow_response()

        # Get access token
        modeller_access_token = self._get_access_token(
            response.auth_code, response.code_verifier, response.redirect_uri
        )

        # Check with Access Manager that user matches expected identity
        # and that the user has the correct permissions for the task
        # that they have requested.
        authentication_result: _PodResponseType = self._check_access(
            modeller_access_token
        )

        logger.info(
            f"OIDC authorisation check complete. "
            f"Will inform modeller: {authentication_result.name}"
        )
        self.pod_response_message.add(authentication_result)
        return self.pod_response_message

    def _get_client_id(self) -> str:
        """Retrieve client ID for pod."""
        # Note: Currently this just returns the static client ID used throughout.
        #       If we change to using Dynamic Client Registration (https://auth0.com/docs/api/authentication#dynamic-application-client-registration)  # noqa: B950
        #       we should change what is returned by this method
        return self._client_id

    def _get_access_token(
        self,
        auth_code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> str:
        """Request access token from oauth endpoint."""
        # POST to endpoint to exchange for access token.
        # See: https://auth0.com/docs/api/authentication?http#authorization-code-flow-with-pkce45  # noqa: B950
        request_data: _PKCEAccessTokenRequestDict = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "code": auth_code,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
        }
        response: Response = web_utils.post(
            self._token_endpoint,
            data=request_data,
            timeout=20,
        )
        response.raise_for_status()

        # Handle good response
        response_json: _PKCEAccessTokenResponseJSON = response.json()
        return response_json["access_token"]

    def _check_access(self, modeller_access_token: str) -> _PodResponseType:
        """Check that access is allowed for the authorised user and request."""
        return self.access_manager.check_oidc_access_request(
            self.pod_response_message.pod_identifier,
            self.serialized_protocol,
            self.mailbox.modeller_name,
            modeller_access_token,
        )


@dataclass
class _OIDCDeviceCode(_AuthorisationChecker[_EncryptedTaskRequest]):
    """OIDC Device Authorisation Flow from pod-side.

    See: https://auth0.com/docs/get-started/authentication-and-authorization-flow/device-authorization-flow  # noqa: B950
    """

    pod_response_message: _PodResponseMessage
    access_manager: BitfountAM
    mailbox: _WorkerMailbox
    serialized_protocol: SerializedProtocol

    # Auth-related params
    _auth_domain: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: B950
    _client_id: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: B950

    def __post_init__(self) -> None:
        # Fill auth-related attributes if not provided
        auth_env = _get_auth_environment()
        if not self._auth_domain:
            self._auth_domain = auth_env.auth_domain
        if not self._client_id:
            self._client_id = auth_env.client_id

        self._token_endpoint: str = f"https://{self._auth_domain}/oauth/token"

    @classmethod
    def _generate_task_request_message(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: List[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
    ) -> bytes:
        return _make_encrypted_task_request_message(
            IdentityVerificationMethod.OIDC_DEVICE_CODE,
            serialized_protocol,
            pod_identifiers,
            aes_key,
            pod_public_key,
        )

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        """See parent class for more information."""
        return cls._generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _EncryptedTaskRequest:
        """See parent class for more information."""
        return _extract_encrypted_task_request(task_request_message)

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        """See parent class for more information."""
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    async def check_authorisation(self) -> _PodResponseMessage:
        """Perform OIDC flow from the pod-side.

        This flow is based on:
        https://auth0.com/docs/get-started/authentication-and-authorization-flow/device-authorization-flow  # noqa: B950
        """
        # Send client ID for pod to modeller
        logger.info("Sending client ID for pod to modeller")
        await self.mailbox.send_oidc_client_id(self._client_id)

        # Wait for device code from modeller
        logger.info("Awaiting identity verification details from modeller")
        device_code_details = await self.mailbox.get_oidc_device_code_response()

        # Poll for user approval/authentication
        logger.info("Awaiting modeller approval for identity verification access")
        modeller_access_token = await self._poll_for_access_token(
            device_code_details.device_code,
            device_code_details.expires_at,
            device_code_details.interval,
        )

        # Check with Access Manager that user matches expected identity
        # and that the user has the correct permissions for the task
        # that they have requested.
        logger.info("Verifying access permissions for modeller task")
        authentication_result: _PodResponseType = self._check_access(
            modeller_access_token
        )

        logger.info(
            f"OIDC authorisation check complete. "
            f"Will inform modeller: {authentication_result.name}"
        )
        self.pod_response_message.add(authentication_result)
        return self.pod_response_message

    async def _poll_for_access_token(
        self, device_code: str, expires_at: datetime, interval: int
    ) -> str:
        """Polls the token endpoint waiting for the authenticated response.

        Polls at the interval specified (which comes from the modeller's
        """
        # Poll until the token has expired
        while self._has_not_expired(expires_at):
            # Make request
            request_data: _DeviceAccessTokenRequestDict = {
                "client_id": self._client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }
            response = web_utils.post(
                self._token_endpoint,
                data=request_data,
                timeout=10,
            )

            # If we get our access token, exit early
            if (status_code := response.status_code) == 200:
                try:
                    success_json: _DeviceAccessTokenResponseJSON = response.json()
                    return success_json["access_token"]
                except (InvalidJSONError, KeyError):
                    raise RequestException(
                        f'Success response, but JSON was invalid: "{response.text}"'
                    )

            # Otherwise, treat as a retry-able error until we know otherwise;
            # status code could be any 4XX value, so we instead just check for the
            # right format and error values.
            try:
                error_json: _DeviceAccessTokenFailResponseJSON = response.json()
            except InvalidJSONError:
                raise RequestException(
                    f'{status_code} response, but JSON was invalid: "{response.text}"'
                )

            # See if just pending authorisation
            if (error := error_json.get("error")) == _AUTHORIZATION_PENDING_ERROR:
                logger.info(
                    "Waiting on modeller to approve identity verification request..."
                )
            # We're requesting too quickly, increase interval
            elif error == _SLOW_DOWN_ERROR:
                logger.warning(
                    f"Polling token endpoint too frequently. "
                    f"Increasing interval from {interval} to {interval+1}"
                )
                interval += 1

            # Otherwise, it's an actual error, raise it
            else:
                # If we have an actual error message, raise that
                if error:
                    error_msg = f"Error in OAuth response ({status_code}) ({error})"
                    # Try to add error_description if present
                    try:
                        error_msg += f": {error_json['error_description']}"
                    except KeyError:
                        pass
                    raise HTTPError(error_msg, response=response)

                # Otherwise, raise an exception with as much detail as possible
                else:
                    raise HTTPError(
                        f"An unexpected error occurred: "
                        f'status code: {status_code}; "{response.text}"'
                    )

            # Sleep for the interval
            await asyncio.sleep(interval)

        # If we're past the expiration, raise it
        raise TimeoutError("Device code has expired, unable to retrieve access token.")

    @staticmethod
    def _has_not_expired(expires_at: datetime) -> bool:
        return datetime.now(timezone.utc) < expires_at

    def _check_access(self, modeller_access_token: str) -> _PodResponseType:
        """Check that access is allowed for the authorised user and request."""
        return self.access_manager.check_oidc_access_request(
            self.pod_response_message.pod_identifier,
            self.serialized_protocol,
            self.mailbox.modeller_name,
            modeller_access_token,
        )


_IDENTITY_VERIFICATION_METHODS_MAP: Final[
    Mapping[IdentityVerificationMethod, Type[_AuthorisationChecker]]
] = {
    # TODO: [BIT-1291] Re-enable KEYS
    # IdentityVerificationMethod.KEYS: _SignatureBasedAuthorisation,
    IdentityVerificationMethod.LOCAL: _LocalAuthorisation,
    IdentityVerificationMethod.OIDC_ACF_PKCE: _OIDCAuthorisationCode,
    IdentityVerificationMethod.OIDC_DEVICE_CODE: _OIDCDeviceCode,
    IdentityVerificationMethod.SAML: _SAMLAuthorisation,
}
