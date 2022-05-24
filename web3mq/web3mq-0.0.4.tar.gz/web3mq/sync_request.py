"""sync request"""
import os
import json

import requests
from requests import codes as http_code

from .singleton_utils import Singleton

from .exception import Web3mqException


class SyncRequestHandler(Singleton):

    def __init__(self, env='prod', base_uri=None):
        if not base_uri:
            if env == 'prod':
                base_uri = 'https://chat.web3messaging.online'
            else:
                base_uri = 'https://test.web3messaging.online'

        self.APP_BASE_API = os.getenv('WEB3MQ_APP_BASE_API', base_uri)

    def do_request(self, method, uri, payload, headers=None, return_raw_result=False):
        if not headers:
            headers = {'Content-Type': 'application/json'}

        url = self.APP_BASE_API + uri

        with requests.sessions.session() as session:
            if method.upper() == 'POST':
                action_cls = session.post
                data = json.dumps(payload)
            elif method.upper() == 'PUT':
                action_cls = session.put
                data = json.dumps(payload)
            elif method.upper() == 'DELETE':
                action_cls = session.delete
                data = json.dumps(payload)
            elif method.upper() == 'GET':
                action_cls = session.get
                data = None
            else:
                action_cls = None
                data = None

            with action_cls(url, data=data, headers=headers) as resp:
                try:
                    result = resp.json()
                except json.JSONDecodeError:
                    result = resp.text

                if resp.status_code == http_code.ok:
                    if return_raw_result:
                        return result
                    else:
                        if result.get('code') == 0:
                            return result.get('data')
                        else:
                            raise Web3mqException(result.get('msg', 'request failure server response without error msg!')) 
                else:
                    raise Web3mqException('request {} failure，status_code:{} result:{}'.format(uri, resp.status_code, result))

        raise Web3mqException('request failure try it again later')

    def get_request(self, uri, payload, headers=None):
        return self.do_request('GET', uri, payload, headers)

    def post_request(self, uri, payload, headers=None, return_raw_result=False):
        return self.do_request('POST', uri, payload, headers, return_raw_result=return_raw_result)
