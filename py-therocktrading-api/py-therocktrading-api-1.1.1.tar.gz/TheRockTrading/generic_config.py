from urllib.parse import urlencode
import hashlib
import time
import hmac


class GenericConfig:        
    def __init__(self, API, API_SECRET, staging):
        self.__url_base_creator(staging)
        self.__api(API, API_SECRET)

    def __api(self, API, API_SECRET):
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

    def _url_creator(self, url_final, **params):
        self.url = self.url_base + url_final
        if url_params := urlencode(params["params"]):
            self.url += "?" + url_params

    def __nonce_creator(self):
        self.__nonce = str(int(time.time()*1000))

    def __signature(self, msg):
        return hmac.new(self.API_SECRET, msg=msg.encode('utf-8'), digestmod=hashlib.sha512).hexdigest()

    def _headers(self):
        self.__nonce_creator()
        return {
            'Content-Type': 'application/json', 
            'X-TRT-KEY': self.API,
            'X-TRT-SIGN': self.__signature(self.__nonce + self.url),
            'X-TRT-NONCE': self.__nonce
        }