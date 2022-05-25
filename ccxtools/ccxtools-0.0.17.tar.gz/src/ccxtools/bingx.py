import base64
import hmac
import json
import requests
import urllib
import urllib.request
from urllib.parse import urljoin
from time import time
from ccxtools.exchange import Exchange


class Bingx(Exchange):

    BASE_URL = 'https://api-swap-rest.bingbon.pro/api/v1'

    def __init__(self, who, market, config):
        super().__init__(market)
        self.API_KEY = config(f'BINGX_API_KEY{who}')
        self.SECRET_KEY = config(f'BINGX_SECRET_KEY{who}')

    def request_get(self, url):
        for i in range(10):
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()

    def request_post(self, url, params):
        for i in range(10):
            params['timestamp'] = int(time()*1000)

            params_str = '&'.join([f'{x}={params[x]}' for x in sorted(params)])

            signature_msg = f'POST/api/v1{url}{params_str}'
            signature = hmac.new(self.SECRET_KEY.encode('utf-8'), signature_msg.encode('utf-8'), 'sha256').digest()

            params_str += '&sign=' + urllib.parse.quote(base64.b64encode(signature))

            request = urllib.request.Request(Bingx.BASE_URL + url, params_str.encode('utf-8'), {'User-Agent': 'Mozilla/5.0'})
            post = urllib.request.urlopen(request).read()

            json_response = json.loads(post.decode('utf-8'))

            if 'invalid timestamp' not in json_response['msg']:
                return json_response
            from pprint import pprint
            pprint(json_response)

    def get_balance(self, ticker):
        params = {
            'apiKey': self.API_KEY,
            'currency': ticker
        }
        response = self.request_post('/user/getBalance', params)
        return response['data']['account']['equity']

    def get_contracts(self):
        url = Bingx.BASE_URL + '/market/getAllContracts'
        return self.request_get(url)
