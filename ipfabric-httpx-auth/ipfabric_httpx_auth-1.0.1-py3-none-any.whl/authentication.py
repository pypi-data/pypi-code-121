import logging
from hashlib import sha512
from typing import Generator
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode, urljoin

import httpx
import jwt

from ipfabric_httpx_auth import oauth2_tokens
from ipfabric_httpx_auth.errors import AuthenticationFailed, GrantNotProvided

logger = logging.getLogger(__name__)


def _add_parameters(initial_url: str, extra_parameters: dict) -> str:
    """
    Add parameters to an URL and return the new URL.

    :param initial_url:
    :param extra_parameters: dictionary of parameters name and value.
    :return: the new URL containing parameters.
    """
    scheme, netloc, path, query_string, fragment = urlsplit(initial_url)
    query_params = parse_qs(query_string)
    query_params.update(
        {parameter_name: [parameter_value] for parameter_name, parameter_value in extra_parameters.items()}
    )

    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def request_new_grant_with_post(url: str, data, client: httpx.Client) -> (str, int):
    response = client.post(url, json=data)

    if response.is_error:
        logger.critical(response.content)
        raise AuthenticationFailed()

    content = response.json()
    token = content.get("accessToken", None)
    refresh_token = data.get("refreshToken", None) or content.get("refreshToken", None)
    if not token:
        raise GrantNotProvided("accessToken", content)
    return token, refresh_token, jwt.decode(token, options={"verify_signature": False})["exp"]


class OAuth2:
    token_cache = oauth2_tokens.TokenMemoryCache()


class PasswordCredentials(httpx.Auth):
    """
    Resource Owner Password Credentials Grant
    """

    def __init__(self, base_url: str, username: str, password: str, **kwargs):
        """
        :param base_url: Base URL.
        :param username: Resource owner user name.
        :param password: Resource owner password.
        :param early_expiry: Number of seconds before actual token expiry where token will be considered as expired.
        Default to 30 seconds to ensure token will not expire between the time of retrieval and the time the request
        reaches the actual server. Set it to 0 to deactivate this feature and use the same token until actual expiry.
        """
        self.base_url = base_url
        if not self.base_url:
            raise SyntaxError("Token URL is mandatory.")
        if not username or not password:
            raise SyntaxError("User name and password is mandatory.")

        self.early_expiry = float(kwargs.pop("early_expiry", None) or 30.0)

        self.data = {
            "username": username,
            "password": password,
        }

        all_parameters_in_url = _add_parameters(self.base_url, self.data)
        self.state = sha512(all_parameters_in_url.encode("unicode_escape")).hexdigest()

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        token = OAuth2.token_cache.get_token(
            self.state, early_expiry=self.early_expiry, on_missing_token=self.request_new_token
        )
        request.headers["Authorization"] = "Bearer {token}".format(token=token)
        yield request

    def request_new_token(self, token: str = None, refresh: str = None) -> tuple:
        client = httpx.Client(headers={"Content-Type": "application/json"})
        if refresh:
            client.headers["Authorization"] = "Bearer {token}".format(token=token)
            data = {"refreshToken": refresh}
            url = urljoin(self.base_url, "/api/v1/auth/token")
        else:
            data = self.data
            url = urljoin(self.base_url, "/api/v1/auth/login")
        try:
            token, refresh_token, expires_in = request_new_grant_with_post(url, data, client)
        finally:
            client.close()
        return self.state, token, refresh_token, expires_in


class HeaderApiKey(httpx.Auth):
    """Describes an API Key requests authentication."""

    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        """
        :param api_key: The API key that will be sent.
        :param header_name: Name of the header field. "X-API-Key" by default.
        """
        self.api_key = api_key
        if not api_key:
            raise SyntaxError("API Key is mandatory.")
        self.header_name = header_name

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[self.header_name] = self.api_key
        yield request
