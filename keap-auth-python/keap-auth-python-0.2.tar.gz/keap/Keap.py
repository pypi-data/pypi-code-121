import base64
from urllib.parse import urlencode

import requests

from keap.KeapToken import KeapToken
from keap.KeapTokenStorage import KeapTokenStorage

try:
    from xmlrpclib import ServerProxy, Error
except ImportError:
    from xmlrpc.client import ServerProxy, Error


class Keap:
    xmlrpc_url = 'https://api.infusionsoft.com/crm/xmlrpc/v1'
    rest_url = 'https://api.infusionsoft.com/crm/rest/v1/'
    authorize_url = 'https://signin.infusionsoft.com/app/oauth/authorize'
    access_token_url = 'https://api.infusionsoft.com/token'
    client = None
    token: KeapToken = None

    def __init__(self, client_id, client_secret, redirect_url, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

        self.use_datetime = kwargs.get('use_datetime', True)
        self.client_name = kwargs.get('client_name', 'default')
        self.token_file = kwargs.get('token_file', './cache/keap_tokens.json')
        self.storage = KeapTokenStorage(self.token_file)
        self.update_client_token_by_client_name(self.client_name)
        self.get_xmlrpc_client(self.token.access_token)

    def get_xmlrpc_client(self, access_token):
        uri = f"{self.xmlrpc_url}?access_token={access_token}"
        self.client = ServerProxy(uri, use_datetime=self.use_datetime, allow_none=True)
        self.client.error = Error
        return self.client

    def __getattr__(self, service):
        def function(method, *args):
            call = getattr(self.client, service + '.' + method)

            try:
                return call(self.token.access_token, *args)
            except self.client.error as v:
                return "ERROR", v

        return function

    def server(self):
        return self.client

    def get_authorization_url(self, state=''):
        if not state:
            state = self.client_name
        data = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url,
            'response_type': 'code',
            'scope': 'full',
            'state': state
        }
        return self.authorize_url + "?" + urlencode(data)

    def request_access_token(self, code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_url,
            'code': code,
            'grant_type': 'authorization_code',
        }

        authorization_token_response = requests.post(self.access_token_url, data)
        self.token = KeapToken(**authorization_token_response.json())
        self.get_xmlrpc_client(self.token.access_token)
        return self.token

    def refresh_access_token(self, client_name=''):
        if client_name and client_name != self.client_name:
            self.update_client_token_by_client_name(client_name)

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.token.refresh_token
        }
        auth_header = "Basic " + base64.b64encode(bytes(f"{self.client_id}:{self.client_secret}", 'utf-8')).decode()
        refresh_token_response = requests.post(self.access_token_url, data, headers={'Authorization': auth_header})
        self.token = KeapToken(**refresh_token_response.json())
        self.get_xmlrpc_client(self.token.access_token)
        return self.token

    def update_client_token_by_client_name(self, client_name):
        self.client_name = client_name
        self.token = self.storage.get_token(self.client_name)

