import time
from typing import Optional

from requests_toolbelt.sessions import BaseUrlSession

from kikyo_api import __version__
from kikyo_api.utils import read_json_data


class KikyoClient:
    def __init__(self, endpoint: str, username: str = None, password: str = None):
        """基于REST API的kikyo客户端

        :param endpoint: REST服务地址
        :param username: 用户名
        :param password: 密码
        """
        if '://' not in endpoint:
            endpoint = f'http://{endpoint}'
        self._endpoint = endpoint
        self._username = username
        self._password = password
        self._login_info: Optional[LoginInfo] = None

        self.session = BaseUrlSession(base_url=self._endpoint)

        from kikyo_api.nsclient.search import SearchClient
        from kikyo_api.nsclient.oss import OssClient

        self.search = SearchClient(self)
        self.oss = OssClient(self)

    def ping(self):
        if self._username:
            if self._login_info is None or self._login_info.is_expired():
                self.session.headers.pop('Authorization', default=None)
                data = read_json_data(
                    self.session.post(
                        '/api/login',
                        json=dict(
                            username=self._username,
                            password=self._password,
                        ),
                        params={
                            'ver': __version__,
                        }
                    )
                )
                self._login_info = LoginInfo(**data)
                self.session.headers.update({
                    'Authorization': f'Bearer {self._login_info.access_token}'
                })


class LoginInfo:
    def __init__(self, access_token: str, expires_in: int, **kwargs):
        self.access_token = access_token
        self.expires_at = time.time() + expires_in - 300

    def is_expired(self) -> bool:
        return time.time() > self.expires_at
