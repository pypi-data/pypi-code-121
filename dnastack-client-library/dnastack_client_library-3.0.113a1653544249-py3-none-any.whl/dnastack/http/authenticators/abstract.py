from abc import ABC
from pydantic import BaseModel
from requests import Request, Session
from requests.auth import AuthBase
from typing import Any, Dict, Union

from dnastack.configuration.models import ServiceEndpoint
from dnastack.http.session_info import SessionInfo


class AuthenticationRequired(RuntimeError):
    """ Raised when the client needs to initiate the authentication process for the first time """


class ReauthenticationRequired(RuntimeError):
    """ Raised when the authenticator needs to initiate the re-authentication process """
    def __init__(self, message: str):
        super().__init__(message)


class ReauthenticationRequiredDueToConfigChange(ReauthenticationRequired):
    """ Raised when the authenticator needs to initiate the re-authentication process due to config change"""


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


class AuthStateStatus:
    READY = 'ready'


class AuthState(BaseModel):
    authenticator: str
    id: str
    auth_info: Dict[str, Any]
    grants: Dict[str, Any]
    status: str  # See AuthStateStatus


class Authenticator(AuthBase, ABC):
    @property
    def fully_qualified_class_name(self):
        t = type(self)
        return f'{t.__module__}.{t.__name__}'

    @property
    def class_name(self):
        return type(self).__name__

    @property
    def session_id(self):
        raise NotImplementedError()

    def initialize(self) -> SessionInfo:
        """ Initialize the authenticator """
        try:
            return self.restore_session()
        except (AuthenticationRequired, ReauthenticationRequired):
            return self.authenticate()
        except RefreshRequired:
            return self.refresh()

    def authenticate(self) -> SessionInfo:
        """ Force-initiate the authorization process """
        raise NotImplementedError()

    def refresh(self) -> SessionInfo:
        """
        Refresh the session

        :raises NoRefreshToken: This indicates that the refresh token is undefined.
        :raises ReauthorizationRequired: The stored session exists but it does not contain enough information to initiate the refresh process.
        :raises FeatureNotAvailable: The feature is not available and the caller may ignore this exception.
        """
        raise NotImplementedError()

    def revoke(self):
        """
        Revoke the session and remove the corresponding session info

        :raises FeatureNotAvailable: The feature is not available and the caller may ignore this exception.
        """
        raise NotImplementedError()

    def restore_session(self) -> SessionInfo:
        """
        Only restore the session info

        :raises AuthenticationRequired: When the authentication is required
        :raised ReauthenticationRequired: When the re-authentication is required
        :raised RefreshRequired: When the token refresh is required
        """
        raise NotImplementedError()

    def before_request(self, r: Union[Request, Session]) -> Union[Request, Session]:
        return self.update_request(self.initialize(), r)

    def update_request(self, session: SessionInfo, r: Union[Request, Session]) -> Union[Request, Session]:
        """ Update the session/request object with session info """
        raise NotImplementedError()

    def get_state(self) -> AuthState:
        """ Retrieve the current state of the authenticator """
        raise NotImplementedError()

    def __call__(self, r: Request):
        self.before_request(r)
        return r

    @classmethod
    def make(cls, endpoint: ServiceEndpoint, auth_info: Dict[str, Any]):
        raise NotImplementedError()