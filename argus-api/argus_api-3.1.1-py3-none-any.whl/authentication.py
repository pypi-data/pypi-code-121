from typing import TYPE_CHECKING, Optional, List, Union
import requests
from argus_api._validators import validate_http_response
from argus_api.utils import _load_cli_settings

if TYPE_CHECKING:
    from argus_api.session import ArgusAPISession


class ArgusAPIAuth:
    """Base authentication class.

    Defines the interface for authentication classes, but should not be used directly
    as does not perform any authentication.
    """

    headers: Optional[dict]
    cookies: Optional[dict]
    is_authenticated: bool = False

    def __call__(self, url):
        return self.headers

    @property
    def headers(self) -> Optional[dict]:
        return None

    @property
    def cookies(self) -> Optional[dict]:
        return None

    def authenticate(self, api_url: str):
        """authenticate the auth object.

        this should perform any required operations (for ex. sending an authentication
        request and retrieving a token) and save all reauired state on the auth object.
        """
        self.is_authenticated = True

    def authenticate_session(self, session: "ArgusAPISession"):
        """authenticate the given session.

        Unlike the authenticate method, this should set the session objects's internal
        session (its :class:`requests.Session` instance) state.
        """
        if not self.is_authenticated:
            self.authenticate(session.base_url)
        if self.headers:
            session._session.headers.update(self.headers)
        if self.cookies:
            session._session.cookies.update(self.cookies)
        session.authenticated = True

    def cleanup_session(self, session: "ArgusAPISession"):
        """Remove authentication state set by the auth object on the given session.

        this is used when changing the authentication object used by a session.
        """
        if self.headers:
            session._session.headers.update({k: None for k in self.headers.keys()})
        session._session.cookies.clear_session_cookies()
        session.authenticated = False

    def __eq__(self, other):
        """Compare two auth objects.

        Comparison is necessary to determine whether authentication settings have
        changed when the argus_cli settings are used.
        """
        return (type(other) is type(self)) and (other is self)


class APIKeyAuth(ArgusAPIAuth):
    """API key authentication interface."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.is_authenticated = True

    @property
    def headers(self) -> dict:
        return {"Argus-API-Key": self.api_key}

    def authenticate_session(self, session: "ArgusAPISession"):
        session._session.headers.update(self.headers)
        session.authenticated = True

    def __eq__(self, other):
        if type(other) == type(self):
            return other.api_key == self.api_key
        return False


class PasswordBasedSessionAuthentication(ArgusAPIAuth):
    """Common password-based session authentication interface.

    This class is an internal utility used to factor functionality common to LDAP and
    password authentication classes.
    """
    DEFAULT_DOMAIN = "MNEMONIC"

    @property
    def cookies(self) -> Optional[dict]:
        return self._cookies

    @property
    def authentication_route(self):
        return f"/authentication/v1/{self.method}/authentication"

    def __init__(
        self,
        method: str,
        username: str,
        password: str,
        domain: Optional[str] = None,
        request_authorizations: Optional[List[str]] = None,
    ):
        """Initialize a PasswordBasedSessionAuthentication object.

        :param method: authentication method - currently either "password" or "ldap"
        :param username: user to authenticate
        :param password: password to authenticate with
        :param request_authorizations: additional special authorizations to request
        """
        if method not in ("password", "ldap"):
            raise ValueError(f"unsupported method: {method}")
        self.method = method
        self.username = username
        self.password = password
        self.domain = domain or self.DEFAULT_DOMAIN
        self.request_authorizations = request_authorizations
        self.session_key = None
        self.session_token = None
        self._cookies = None
        self.is_authenticated = False

    def _post_auth(
        self, session_or_base_url: Union["ArgusAPISession", str], mutate_session=True
    ):
        """perform the authentication request.

        :param session_or_base_url: either a session object or the API base URL.
           if ``mutate_session`` is set to ``True``, must be a session object.
       :param mutate_session: if set to ``True``, will set authentication state
          (cookies) on the session.
        """
        if isinstance(session_or_base_url, str):
            base_url = session_or_base_url
            if mutate_session:
                raise ValueError("can not mutate session, a base URL was passed.")
        else:
            base_url = session_or_base_url.base_url
        url = f"{base_url}{self.authentication_route}"
        payload = {
            "userName": self.username,
            "password": self.password,
            "domain": self.domain,
        }
        if self.request_authorizations:
            payload["requestedAuthorizations"] = self.request_authorizations
        if mutate_session:
            response = session_or_base_url._session.post(url, json=payload)
        else:
            response = requests.post(url, json=payload)
        validate_http_response(response)
        return response

    def authenticate(self, api_url: str):
        response = self._post_auth(api_url, mutate_session=False)
        self._cookies = dict(response.cookies)
        rdata = response.json()
        self.session_key = rdata["data"]["sessionKey"]
        self.session_token = rdata["data"]["credentials"]["requestCredentialsData"]
        self.is_authenticated = True

    def authenticate_session(self, session: "ArgusAPISession"):
        response = self._post_auth(session, mutate_session=True)

        rdata = response.json()
        self.session_key = rdata["data"]["sessionKey"]
        self.session_token = rdata["data"]["credentials"]["requestCredentialsData"]
        self.is_authenticated = True
        session.authenticated = True

    def __eq__(self, other):
        if type(other) == type(self):
            return all(
                [
                    (other.method == self.method),
                    (other.username == self.username),
                    (other.password == self.password),
                    (other.domain == self.domain),
                ]
            )
        return False


class PasswordAuthentication(PasswordBasedSessionAuthentication):
    """Password authentication."""
    def __init__(
        self,
        username: str,
        password: str,
        domain: Optional[str] = None,
        request_authorizations: Optional[List[str]] = None,
    ):
        """Initialize a PasswordAuthentication object.

        :param username: user to authenticate
        :param password: password to authenticate with
        :param request_authorizations: additional special authorizations to request
        """
        super().__init__(
            method="password",
            username=username,
            password=password,
            domain=domain,
            request_authorizations=request_authorizations,
        )


class LDAPAuthentication(PasswordBasedSessionAuthentication):
    def __init__(
        self,
        username: str,
        password: str,
        domain: Optional[str] = None,
        request_authorizations: Optional[List[str]] = None,
    ):
        """Initialize a PasswordAuthentication object.

        :param username: user to authenticate
        :param password: password to authenticate with
        :param request_authorizations: additional special authorizations to request
        """
        super().__init__(
            method="ldap",
            username=username,
            password=password,
            domain=domain,
            request_authorizations=request_authorizations,
        )


def get_auth_from_cli_config() -> ArgusAPIAuth:
    """construct an authentication object from argus_cli settings."""
    settings = _load_cli_settings()
    api_settings = settings.get("api", {})
    method = api_settings.get("method", "apikey")
    if method == "apikey":
        api_key = api_settings.get("api_key")
        return APIKeyAuth(api_key=api_key)
    elif method in ("password", "ldap"):
        username = api_settings.get("username")
        password = api_settings.get("password")
        domain = api_settings.get("domain")
        if method == "password":
            cls = PasswordAuthentication
        elif method == "ldap":
            cls = LDAPAuthentication
        return cls(username=username, password=password, domain=domain)
