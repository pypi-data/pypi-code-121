from abc import ABC
from typing import Any, Dict, Union

from requests import Request, Session
from requests.auth import AuthBase

from dnastack.http.session_info import SessionInfo
from dnastack.configuration.models import ServiceEndpoint


class AuthenticationRequired(RuntimeError):
    """ Raised when the client needs to initiate the authentication process for the first time """


class ReauthenticationRequired(RuntimeError):
    """ Raised when the authenticator needs to initiate the re-authentication process """
    def __init__(self, message: str):
        super().__init__(message)


class RetryWithFallbackAuthentication(RuntimeError):
    """ Raised when the authenticator needs to use a fallback authorization before retrying """


class RefreshRequired(RuntimeError):
    """ Raised when the authenticator needs to initiate the refresh process """
    def __init__(self):
        super().__init__('Session refresh required')


class NoRefreshToken(RuntimeError):
    """ Raised when the authenticator attempts to refresh tokens but the refresh token is not defined """
    def __init__(self):
        super().__init__('No refresh token')


class FeatureNotAvailable(RuntimeError):
    """ Raised when the authenticator does not support a particular feature. This can be safely ignored. """
    def __init__(self):
        super().__init__('Feature not available')


class InvalidStateError(RuntimeError):
    pass


class Authenticator(AuthBase, ABC):
    def authenticate(self) -> SessionInfo:
        raise NotImplementedError()

    def refresh(self) -> SessionInfo:
        """
        :raises NoRefreshToken: This indicates that the refresh token is undefined.
        :raises ReauthorizationRequired: The stored session exists but it does not contain enough information to initiate the refresh process.
        :raises FeatureNotAvailable: The feature is not available and the caller may ignore this exception.
        """
        raise NotImplementedError()

    def revoke(self):
        """
        :raises FeatureNotAvailable: The feature is not available and the caller may ignore this exception.
        """
        raise NotImplementedError()

    def before_request(self, r: Union[Request, Session]):
        raise NotImplementedError()

    def __call__(self, r: Request):
        self.before_request(r)
        return r

    @classmethod
    def make(cls, endpoint: ServiceEndpoint, auth_info: Dict[str, Any]):
        raise NotImplementedError()