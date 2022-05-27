import requests
import json
import jwt
from .errors import LoginIDError

import random
from datetime import datetime

from typing import Optional

class _LoginIdClient():
    DEFAULT_JWT_ALOGORITHM = 'ES256'
    SUPPORTED_JWT_ALGORITHMS = {DEFAULT_JWT_ALOGORITHM}
    DEFAULT_BASE_URL = "https://directweb.usw1.loginid.io"

    ALLOWED_CODE_TYPES = {'short', 'long', 'phrase'}

    # leeway is in seconds
    JWT_LEEWAY = 60

    def __init__(self, client_id: str, private_key: Optional[str]=None, base_url: Optional[str]=None) -> None:
        self._private_key = private_key
        self._client_id = client_id
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip('/')

    def client_id(self) -> str:
        """Extract the client id

        Returns:
            str: The client id
        """
        return self._client_id

    def _get_utc_epoch(self):
        """
        returns the current UTC epoch in seconds
        """
        return int((datetime.utcnow()-datetime(1970, 1, 1)).total_seconds())

    def _random_string(self, length: int = 16) -> str:
        """
        Generate a random string of given length with alphanumeric characters

        Args:
            length (int): length of the output string

        Returns:
            str: a random string
        """
        possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        ret = [random.choice(possible) for _ in range(length)]
        return "".join(ret)

    def _get_public_key(self, kid: Optional[str] = None) -> str:
        """Return the server's public key with `kid`

        Args:
            kid (str, optional): the kid included in jwt's header. Defaults to "".

        Returns:
            str: The public key in PEM format
        """
        # ensure kid is not None
        kid = kid or ""

        params = {"kid": kid} if kid else None

        r = requests.get(f'{self._base_url}/certs', params=params)
        if (r.status_code != 200):
            error = r.json()
            raise LoginIDError(
                r.status_code,
                error.get('code', 'UNKNOWN_ERROR'),
                error.get('message', 'Unknown Error')
            )

        # TODO: cache the public key
        return r.text

    def _update_payload(self, payload: dict, user_id: Optional[str] = None, username: Optional[str] = None) -> None:
        """Update payload with user_id and username if present

        Args:
            payload (dict): payload to be updated
            user_id (str, optional): user id to be updated. Defaults to None.
            username (str, optional): username to be updated. Defaults to None.
        """

        # verify that either user_id or username is present
        if not (user_id or username):
            raise LoginIDError(
                400, "bad_request", "either `user_id` or `username` must be present")

        if user_id:
            payload['user_id'] = user_id
        if username:
            payload['username'] = username

    def _request(self, method: str, url: str, token_scope: Optional[str] = None,
                 payload: Optional[dict] = None, params: Optional[dict] = None,
                 headers: Optional[dict] = None, expect=200) -> dict:
        """
        Make a request to the LoginID service
        """
        methods = {
            'post': requests.post,
            'get': requests.get,
            'put': requests.put,
            'delete': requests.delete
        }
        r_method = methods.get(method.lower(), None)
        if r_method is None:
            raise LoginIDError(400, "INVALID_METHOD", "Invalid method")

        if headers is None:
            headers = headers or {
                "Content-type": "application/json",
                "X-Client-ID": self._client_id
            }
            if self._private_key:
                headers['Authorization'] = f"Bearer {self.generate_service_token(token_scope)}"

        _url = f'{self._base_url}{url}'
        if payload is not None:
            r = r_method(_url, data=json.dumps(payload), headers=headers)
        else:
            r = r_method(_url, params=params, headers=headers)

        if (r.status_code != expect):
            try:
                error = r.json()
            except Exception:
                raise LoginIDError(500, 'UNKNOWN_ERROR', r.text)

            raise LoginIDError(
                r.status_code,
                error.get('code', 'UNKNOWN_ERROR'),
                error.get('message', r.text or "Unknown error")
            )
        # only return json if there is a response
        return r.json() if expect != 204 else {}

    def verify_token(self, token: str, username: Optional[str] = None) -> bool:
        """Verify a JWT token returned upon user authorization

        Args:
            token (str): JWT token
            username (str, optional): if given, checks for if `username` matches the `udata` in JWT. Defaults to None.

        Returns:
            bool: `True` if the token is valid, `False` otherwise (including errors)
        """

        headers = jwt.get_unverified_header(token)

        # extract algo, kid from headers, default to None
        algo, kid = headers.get('alg'), headers.get('kid')

        # verify that algo is supported
        if algo not in self.SUPPORTED_JWT_ALGORITHMS:
            raise LoginIDError(400, "invalid_algorithm", f"{algo} is not an allowed algorithm.")

        # obtain public key from LogInID
        public_key = self._get_public_key(kid)

        payload = jwt.decode(
            token, public_key,
            algorithms=self.SUPPORTED_JWT_ALGORITHMS,
            audience=self._client_id,
            leeway=self.JWT_LEEWAY
        )

        if username is not None:
            return username == payload['udata']
        return True

    def generate_service_token(self, scope: str,
                               username: Optional[str] = None, user_id: Optional[str] = None,
                               algo: Optional[str] = None, nonce: Optional[str] = None) -> str:
        """
        Generate a service token

        Args:
            scope (str): the scope of the service
            username (str, optional): the username to-be granted by the token
            user_id (str, optional): the user_id to be granted by the token. If `username` is given, this is ignored
            algo (str, optional): Encryption algorithm, defaults to `"ES256"`
            nonce (str, optional): nonce for the token, randomly generated if not given

        Returns:
            str: the JWT service token if `self._private_key` is set, else the empty string.
        """

        # only generate service token if private key is set
        if not self._private_key:
            return ""

        algo = algo or self.DEFAULT_JWT_ALOGORITHM
        if algo not in self.SUPPORTED_JWT_ALGORITHMS:
            raise LoginIDError(400, "invalid_algorithm", f"{algo} is not an allowed algorithm.")

        payload = {
            "client_id": self._client_id,
            "type": scope,
            "nonce": nonce or self._random_string(16),
            "iat": self._get_utc_epoch()
        }

        if username is not None:
            payload['username'] = username
        elif user_id is not None:
            payload['user_id'] = user_id

        jwt_headers = {"alg": algo, "typ": "JWT"}

        try:
            return jwt.encode(
                payload, self._private_key, algorithm=algo,
                headers=jwt_headers
            )
        except Exception as e:
            raise LoginIDError(500, "SERVER_ERROR",
                               f'Failed to generate service token {e}')
