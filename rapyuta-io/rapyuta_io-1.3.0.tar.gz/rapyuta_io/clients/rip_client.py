from __future__ import absolute_import
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import get_api_response_data


class RIPClient:
    AUTH_TOKEN_PATH = '/user/login'

    def __init__(self, rip_host):
        self._rip_host = rip_host

    def get_auth_token(self, email, password):
        url = self._rip_host + self.AUTH_TOKEN_PATH
        payload = {'email': email, 'password': password}
        response = RestClient(url).method(HttpMethod.POST).query_param({'type': 'high'}).execute(payload)
        data = get_api_response_data(response, parse_full=True)
        return data['data']['token']
