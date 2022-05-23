from typing import Union, Optional, List

from utils.Logger import Logger
from connectors.CurlConnectorInterface import CurlInterface
import collections
import urllib.parse
import pycurl
import time

from json import dumps, loads


class CurlConnector(CurlInterface):
    """This is a class for curl connector.

        Options for curl object are set by default
        but you can override them -> see CurlConnectorInterface
    """

    _COOKIE_FILE = '/tmp/proxyidp_cookie.txt'

    _CONNECT_TIMEOUT = 1

    _TIMEOUT = 15

    def __init__(
            self, url: str,
            params: dict[
                str, Union[str, Optional[int], bool,
                           List[str], dict[str, str]]]
    ):
        if params is None:
            params = []

        self._connection = pycurl.Curl()
        self.url = url
        self.params = params
        self._logger = Logger.get_logger(self.__class__.__name__)

        self._connection.setopt(pycurl.COOKIEJAR, self._COOKIE_FILE)
        self._connection.setopt(pycurl.COOKIEFILE, self._COOKIE_FILE)
        self._connection.setopt(pycurl.CONNECTTIMEOUT, self._CONNECT_TIMEOUT)
        self._connection.setopt(pycurl.TIMEOUT, self._TIMEOUT)

    def setopt_userpwd(self, user, password):
        self._connection.setopt(pycurl.USERPWD, user + ':' + password)

    def setopt_cookiejar(self, cookie_file):
        self._connection.setopt(pycurl.COOKIEJAR, cookie_file)

    def setopt_cookiefile(self, cookie_file):
        self._connection.setopt(pycurl.COOKIEFILE, cookie_file)

    def setopt_connecttimeout(self, connect_timeout):
        self._connection.setopt(pycurl.CONNECTTIMEOUT, connect_timeout)

    def setopt_timeout(self, timeout):
        self._connection.setopt(pycurl.TIMEOUT, timeout)

    def get(self):
        params_query = self._http_build_query(self.params)

        self._connection.setopt(pycurl.CUSTOMREQUEST, 'GET')
        self._connection.setopt(pycurl.URL, self.url + '?' + params_query)

        start_time = time.time()
        json = self._connection.perform_rs()
        end_time = time.time()

        response_time = round(end_time - start_time, 3)
        self._logger.debug('curl: GET call', self.url, 'with params:',
                           params_query, 'response :', json, 'in',
                           str(response_time) + 's.')

        return self._execute_request("GET", params_query, json)

    def post(self):
        params_json = dumps(self.params)

        self._connection.setopt(pycurl.URL, self.url)
        self._connection.setopt(pycurl.CUSTOMREQUEST, 'POST')
        self._connection.setopt(pycurl.POSTFIELDS, params_json)
        self._connection.setopt(
            pycurl.HTTPHEADER,
            ['Content-Type:application/json',
             'Content-Length: ' + str(len(params_json))]
        )

        start_time = time.time()
        json = self._connection.perform_rs()
        end_time = time.time()

        response_time = round(end_time - start_time, 3)
        self._logger.debug('curl: POST call', self.url, 'with params:',
                           params_json, 'response :', json, 'in',
                           str(response_time) + 's.')

        result = self._execute_request("POST", params_json, json)

        self._connection.unsetopt(pycurl.HTTPHEADER)
        self._connection.unsetopt(pycurl.CUSTOMREQUEST)

        return result

    def _execute_request(self, request_type, params, json):
        if not json:
            raise Exception('Cant\'t get response from Url. Call: '
                            + self.url + ', Params: ' + params
                            + ', Response: ' + json
                            )
        try:
            result = loads(json)
            return result
        except ValueError:
            self._logger.warning(f'curl: {request_type} call failed. Call: '
                                 + self.url + ', Params: ' + params
                                 + ', Response: ' + json)

    @staticmethod
    def _http_build_query(data):
        dct = collections.OrderedDict()
        for key, value in data.items():
            if isinstance(value, list):
                for index, element in enumerate(value):
                    dct['{0}[{1}]'.format(key, index)] = element
            else:
                dct[key] = str(value)
        return urllib.parse.urlencode(dct)

    def __del__(self):
        self._connection.close()
