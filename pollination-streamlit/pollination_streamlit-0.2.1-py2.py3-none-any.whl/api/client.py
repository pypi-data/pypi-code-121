import typing as t
from io import BytesIO

import requests
from requests import Session

# from ._client_base import ClientBase as Client

DEFAULT_HOST = 'https://api.pollination.cloud'


class ApiClient():

    def __init__(self, host: str = DEFAULT_HOST, api_token: str = None, jwt_token: str = None):
        if host[-1] == '/':
            host = host[:-1]

        self._host = host
        self.api_token = api_token
        self.jwt_token = jwt_token

    @property
    def host(self) -> str:
        return self._host

    @property
    def headers(self):
        if self.api_token is not None:
            return {
                'x-pollination-token': self.api_token
            }
        elif self.jwt_token is not None:
            return {
                'Authorization': f'Bearer {self.jwt_token}'
            }
        return {}

    @property
    def session(self):
        s = Session()
        s.headers = self.headers
        return s

    def _url_path(self, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        return self.host + path

    def get(self, path: str, params: t.Dict[str, t.Any] = {}) -> t.Dict[str, t.Any]:
        res = self.session.get(url=self._url_path(path), params=params)
        res.raise_for_status()
        try:
            return res.json()
        except:
            return res.text

    def post(self, path: str, json: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        res = self.session.post(url=self._url_path(path), json=json)
        res.raise_for_status()
        try:
            return res.json()
        except:
            return res.text

    def download_artifact(self, signed_url: str) -> BytesIO:
        res = requests.get(signed_url)
        res.raise_for_status()
        return BytesIO(res.content)
