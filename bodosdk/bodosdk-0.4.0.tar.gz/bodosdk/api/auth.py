from datetime import datetime

import jwt

from bodosdk.api.request_wrapper import RequestWrapper
from bodosdk.exc import Unauthorized
from bodosdk.models.base import APIKeys


class AuthApi:

    def __init__(self, auth: APIKeys, auth_url='https://prod-auth.bodo.ai', requests=RequestWrapper()):
        self._requests = requests
        self._auth_url = auth_url
        self._auth = auth
        self._token = None

    def _authenticate(self):
        resp = self._requests.post(
            f"{self._auth_url}/identity/resources/auth/v1/api-token",
            json={
                "clientId": self._auth.client_id,
                "secret": self._auth.secret_key,
            },
        )
        if resp.status_code == 200:
            return resp.json()["accessToken"]
        raise Unauthorized

    def switch_workspace(self, auth: APIKeys):
        self._auth = auth
        self._token = self._authenticate()

    @property
    def auth_token(self):
        try:
            exp = datetime.fromtimestamp(jwt.decode(self._token, options={"verify_signature": False})['exp'])
            if exp < datetime.now():
                self._token = self._authenticate()
        except Exception as ex:
            self._token = self._authenticate()
        return self._token
