from datetime import datetime, timedelta
from functools import wraps
from logging import getLogger
from dataclasses import dataclass, field

import jwt
import requests


logger = getLogger(__name__)


@dataclass
class TokenClient:
    """Client base class which handles authentication via the Tokens API.

    This is mostly just a wrapper around the requests library, which updates
    request headers with a JWT from the Tokens API for authentication.

    The TokenClient can create its own token, rather than querying an API,
    if the secret key required to create the token is available - DO THIS AT
    YOUR OWN RISK.

    Uses the same logic as the Tokens API, so can be used with local
    HIRMEOS projects, such as the translator, and any drivers.

    Note: This only works for projects where you run the tokens API or
    service which runs the authentication (metrics-api, translator, etc).
    """
    tokens_api_endpoint: str = field(repr=False, default='')
    tokens_username: str = field(repr=False, default='')
    tokens_password: str = field(repr=False, default='')

    tokens_key: str = field(repr=False, default='')
    tokens_email: str = field(repr=False, default='')
    tokens_name: str = field(repr=False, default='')
    tokens_account: str = field(repr=False, default='')

    jwt_disabled: bool = field(repr=False, default=False)
    ignore_cache: bool = field(default=False)  # Set to True for testing.

    token: str = ''

    def __post_init__(self):
        """Set tokens Authorization header and add it to client requests."""
        self.header = {}

        if not self.jwt_disabled:
            self.set_auth_header()

        self.delete = self.authenticated_request(requests.delete)
        self.get = self.authenticated_request(requests.get)
        self.patch = self.authenticated_request(requests.patch)
        self.post = self.authenticated_request(requests.post)
        self.put = self.authenticated_request(requests.put)

        self._cache = {}.copy()  # prevent repeating queries

    def clear_cache(self):
        self._cache.clear()

    def get_token(self):
        """Fetch token from Tokens API."""

        if self.jwt_disabled:
            return ''

        credentials = {
            'email': self.tokens_username,
            'password': self.tokens_password
        }
        response = requests.post(self.tokens_api_endpoint, json=credentials)

        if response.status_code != 200:
            raise ValueError(response.content.decode('utf-8'))

        return response.json()['data'][0]['token']

    def create_token(self):
        """Create a JWT."""

        token_content = {
            'authority': 'admin',
            'email': self.tokens_email,
            'exp': datetime.utcnow() + timedelta(minutes=15),  # adjustable?
            'iat': datetime.utcnow(),
            'name': self.tokens_name,
            'sub': self.tokens_account
        }
        token = jwt.encode(token_content, self.tokens_key)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token

    def set_token(self):
        """Fetch or create token to be used for requests."""
        if self.tokens_key:
            self.token = self.create_token()

        else:
            token_requirements = (
                self.tokens_api_endpoint,
                self.tokens_username,
                self.tokens_password,
            )

            if not all(token_requirements):
                raise TypeError(
                    "'jwt_disabled' has been set to 'False'. "
                    "Please specify tokens_api endpoint and login credentials."
                )

            self.token = self.get_token()

    def set_auth_header(self, token_has_expired=False):
        """Sets Authorization header for the client using the Bearer schema.

        Args:
            token_has_expired (bool): True if token has expired.
        """
        if not self.token or token_has_expired:
            self.set_token()

        self.header.update(Authorization=f'Bearer {self.token}')

    def authenticated_request(self, func):
        """Decorator to add token authentication to requests."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.setdefault('headers', {}).update(self.header)
            response = func(*args, **kwargs)

            if response.status_code == 401:  # Assume token has expired
                self.set_auth_header(token_has_expired=True)
                kwargs['headers'].update(self.header)
                response = func(*args, **kwargs)

            return response

        return wrapper

    def __str__(self):
        return self.__class__.__name__
