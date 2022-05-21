import json
import requests
from simplejson.errors import JSONDecodeError

import mapnamindsdk.Constants as Constants
from requests import Session, RequestException


class Rest(Session):

    def __init__(self,
                 base_url: str = f'{Constants.GATEWAY_SERVER_IP}:{Constants.GATEWAY_PORT}',
                 path: str = '/',
                 params: dict = None,
                 header: dict = {'Content-Type': 'application/json; charset=utf-8'},
                 response_encoding: str = 'utf-8'):

        super().__init__()

        self.base_url = base_url
        self.path = path
        self.params = params
        self.header = header
        self.response_encoding = response_encoding

        pass

    def _do_it(self, verb: str = 'get', get_json: bool = True):

        try:
            full_url = f'{self.base_url}{self.path}'

            if verb == 'get':
                response = requests.request(method=verb, url=full_url, headers=self.header, params=self.params)
            else:
                response = requests.request(
                    method=verb, url=full_url, headers=self.header, data=json.dumps(self.params))
            return response.json() if get_json and response else response.text
        except JSONDecodeError as jerr:
            print('JSON Decode Error:', str(jerr))
        except RequestException as rerr:
            print(
                f'Request Exception:\n Message:{str(rerr)}')
        return None

    def get(self, get_json: bool = True):
        return self._do_it('get', get_json)

    def post(self, get_json: bool = True):
        return self._do_it('post', get_json)

    def put(self, get_json: bool = True):
        return self._do_it('put', get_json)

    def delete(self, get_json: bool = True):
        return self._do_it('delete', get_json)

    def head(self, get_json: bool = True):
        return self._do_it('head', get_json)


if __name__ == "__main__":

    params = {"par1": "value1", "par2": "take it easy"}

    # req = Rest(base_url='https://localhost:7175/test',
    #            path='/get', params=params)

    post_req = Rest(base_url='http://localhost:7175',
                    path='/test', params=params)

    # print(post_req.do_it('POST'))

  # print(req.get())
    print(post_req.post())

    pass
