"""Types for hub-related code."""
from typing import Literal, TypedDict, Union

from bitfount.federated.types import SerializedProtocol
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL


# General JSONs
class _HubSuccessResponseJSON(TypedDict):
    """Generic hub success response JSON."""

    success: Literal[True]
    message: str


class _HubFailureResponseJSON(TypedDict):
    """Generic hub failure response JSON."""

    success: Literal[False]
    errorMessage: str


_HubResponseJSON = Union[_HubSuccessResponseJSON, _HubFailureResponseJSON]


# Hub-related JSON.
class _PodDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/pods/[userName]/[podName]."""

    podIdentifier: str
    podName: str
    podDisplayName: str
    podPublicKey: str
    accessManagerPublicKey: str
    description: str
    # dataSchema: str  # present but should not be used
    schemaStorageKey: str
    isOnline: bool
    providerUserName: str
    visibility: Literal["public", "private"]
    schemaDownloadUrl: _S3PresignedURL


class _MultiPodDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/pods."""

    podIdentifier: str
    name: str
    podDisplayName: str
    isOnline: bool
    podPublicKey: str
    accessManagerPublicKey: str
    description: str
    providerUserName: str
    podPagePath: str


class _PodRegistrationResponseJSON(TypedDict):
    """Response JSON from POST /api/pods."""

    success: bool
    alreadyExisted: bool
    message: str
    uploadUrl: _S3PresignedPOSTURL
    uploadFields: _S3PresignedPOSTFields


class _PodRegistrationFailureJSON(TypedDict):
    """Failure response JSON from POST /api/pods."""

    success: Literal[False]
    alreadyExisted: bool
    errorMessage: str


class _ModelDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/models when getting specific model."""

    modelStorageKey: str
    modelDownloadUrl: _S3PresignedURL


class _MultiModelDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/models when getting all models."""

    modellerName: str
    modelName: str
    modelStorageKey: str


class _ModelUploadResponseJSON(TypedDict):
    """Response JSON from POST /api/models."""

    # This is not a 1-to-1 mapping with the actual return types (i.e. some are
    # only returned on success, some only on failure), but is enough for our
    # use case.
    uploadUrl: _S3PresignedPOSTURL
    uploadFields: _S3PresignedPOSTFields
    success: bool
    errorMessage: str


# Access Manager-related JSON
class _AccessManagerKeyResponseJSON(TypedDict):
    """Response JSON from GET /api/access-manager-key."""

    accessManagerPublicKey: str


class _SAMLChallengeResponseJSON(TypedDict):
    """Response JSON from GET /api/saml."""

    samlRequest: str
    id: str


class _SAMLAdditionalInfoPOSTJSON(TypedDict):
    """Required keys for JSON POST /api/saml."""

    # If this issue gets resolved then we can actually add the SAML response
    # fields to this as extras: https://github.com/python/mypy/issues/4617
    originalSAMLRequestID: str
    podIdentifier: str
    modellerName: str
    modellerProtocolRequest: SerializedProtocol
    identityProvider: Literal["SAML"]


class _OIDCAccessCheckPostJSON(TypedDict):
    """Required keys for OIDC JSON POST /api/access."""

    podIdentifier: str
    modellerProtocolRequest: SerializedProtocol
    modellerName: str
    modellerToken: str
    identityProvider: Literal["OIDC"]


class _AMAccessCheckResponseJSON(TypedDict):
    """Response JSON from Access Manager access check.

    Covers:
        - POST /api/access
    """

    # TODO: [BIT-1291] Remove old response types
    code: Literal[
        # Common response types
        "ACCEPT",
        # Old style response types
        "ACCESS_MANAGER_NOT_AUTHORISED",
        "PROTOCOL_NOT_APPROVED",
        "MODELLER_SIGNATURE_DOES_NOT_MATCH",
        "SECURE_AGGREGATION_WORKERS_NOT_AUTHORISED",
        "ACCESS_REQUEST_NOT_APPROVED",
        "USER_ID_DOES_NOT_MATCH_APPROVED_USER",
        "CANNOT_VERIFY_ACCESS_REQUEST",
        "NO_ACCESS_REQUESTS",
        "ERROR_IN_VERIFICATION",
        # /api/access response types
        "NO_ACCESS",
        "INVALID_PROOF_OF_IDENTITY",
        "UNAUTHORISED",
        "NO_PROOF_OF_IDENTITY",
    ]


# Auth0 related types
class _DeviceCodeRequestDict(TypedDict):
    """Data dictionary for POST request to /oauth/device/code.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow
    """

    audience: str
    scope: str
    client_id: str


class _DeviceCodeResponseJSON(TypedDict):
    """JSON response for POST /oauth/device/code.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow
    """

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class _DeviceAccessTokenRequestDict(TypedDict):
    """Data dictionary for device code POST request to /oauth/token.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48
    """

    grant_type: Literal["urn:ietf:params:oauth:grant-type:device_code"]
    client_id: str
    device_code: str


class _DeviceAccessTokenResponseJSON(TypedDict):
    """Success JSON response for POST /oauth/token.

    For Device Authorization Flow.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48
    """

    access_token: str
    id_token: str
    refresh_token: str
    scope: str
    expires_in: int
    token_type: Literal["Bearer"]


class _TokenRefreshRequestDict(TypedDict):
    """Data dictionary for token refresh POST request to /oauth/token.

    This is not the full potential params, but is enough for us.

    See: https://auth0.com/docs/api/authentication?http#refresh-token
    """

    grant_type: Literal["refresh_token"]
    client_id: str
    refresh_token: str


class _TokenRefreshResponseJSON(TypedDict):
    """Success JSON response for refresh token POST /oauth/token.

    See: https://auth0.com/docs/api/authentication?http#refresh-token

    Note that our response will include a new refresh token as we are using
    refresh token rotation.

    See: https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation
    """

    access_token: str
    id_token: str
    refresh_token: str  # see docstring
    scope: str
    expires_in: int
    token_type: Literal["Bearer"]


class _DeviceAccessTokenFailResponseJSON(TypedDict):
    """Fail JSON response for POST /oauth/token.

    For Device Authorization Flow.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48
    """

    error: str
    error_description: str


class _PKCEAccessTokenRequestDict(TypedDict):
    """Data dictionary for ACF with PKCE code POST request to /oauth/token.

    See: https://auth0.com/docs/api/authentication?http#authorization-code-flow-with-pkce45  # noqa: B950
    """

    grant_type: Literal["authorization_code"]
    client_id: str
    code: str
    code_verifier: str
    redirect_uri: str


class _PKCEAccessTokenResponseJSON(TypedDict):
    """Success JSON response for POST /oauth/token.

    For Authorization Code Flow with PKCE.

    See: https://auth0.com/docs/api/authentication?http#authorization-code-flow-with-pkce45  # noqa: B950
    """

    access_token: str
    refresh_token: str
    id_token: str
    token_type: Literal["Bearer"]
    expires_in: int
