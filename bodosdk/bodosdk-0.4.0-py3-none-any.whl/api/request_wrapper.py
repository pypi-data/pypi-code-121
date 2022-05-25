from pprint import pprint
from time import sleep

import requests


class RequestWrapper:

    def __init__(self, print_logs=False):
        self.print_logs = print_logs

    def get(self, *args, **kwargs):
        return self._request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request('POST', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request('DELETE', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request('PUT', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request('PATCH', *args, **kwargs)

    def _request(self, method, *args, **kwargs):
        try:
            if self.print_logs:
                pprint(args[1:])
                pprint(kwargs)
            return requests.request(method, *args, **kwargs)
        except requests.exceptions.ConnectionError as ex:
            if self.print_logs:
                pprint(ex)
            sleep(1)
            return self.get(*args, **kwargs)