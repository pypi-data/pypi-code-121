from urllib.parse import urlencode, quote_plus
import hashlib
import httpx
import json
import time
import hmac
import os

class Config:        
    def configuration(self, API, API_SECRET, staging):
        self.__url_base_creator(staging)
        self.__api(API, API_SECRET, staging)
        self.__client = httpx.Client(headers=self.__headers_init(), limits=httpx.Limits(max_connections=10))


    def __exit__(self):
        self.__client.close()
                

    def __api(self, API, API_SECRET, staging):
        self.API = API
        self.API_SECRET = API_SECRET.encode('utf-8')


    def __url_base_creator(self, staging):
        endpoint_staging = 'https://api-staging.therocktrading.com'
        endpoint = 'https://api.therocktrading.com'
        host = '/v1'

        if staging:
            self.url_base = endpoint_staging + host
        else:
            self.url_base = endpoint + host


    def __unzip_params(self, params):
        if params:
            return params['params']
        else:
            return ''


    def url_creator(self, url_final, **params):
        params = self.__unzip_params(params)
        self.url = self.url_base + url_final + urlencode(params)


    def __headers_init(self):
        return {'Content-Type': 'application/json', 'X-TRT-KEY': self.API}


    def __nonce_creator(self):
        self.__nonce = str(int(time.time()*1000))


    def __signature(self, msg):
        return hmac.new(self.API_SECRET, msg=msg.encode('utf-8'), digestmod=hashlib.sha512).hexdigest()


    def __headers(self):
        self.__nonce_creator()
        self.__client.headers['X-TRT-SIGN'] = self.__signature(self.__nonce + self.url)
        self.__client.headers['X-TRT-NONCE'] = self.__nonce


    def requests_and_parse(self, method):
        self.__headers()
        response = self.__client.send(self.__client.build_request(method, self.url)).json()
        return response