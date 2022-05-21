import logging
from dataclasses import dataclass
from typing import Callable, Any

import requests

from . import utils, errors
from .filters import Filter

Func = Callable[[], Any]

API_ENDPOINT = 'https://api.telegram.org/bot{token}/{method}'


@dataclass
class Handler:
    func: Func
    filters: list[Filter]


class Bot:
    def __init__(self):
        self.handlers: list[Handler] = []
        self.session = requests.Session()

    def add_handler(self, func: Func, filters: list[Filter] = None):
        handler = Handler(func, filters or [])
        self.handlers.append(handler)

    def request(self, method: str, params: dict) -> dict | list | bool | str | int:
        from .loader import ctx

        params = utils.clear_params(params)
        url = API_ENDPOINT.format(token=ctx.token, method=method)

        logging.debug(f'Request {method} with params: {params}')
        resp = self.session.post(url, json=params)
        result: dict = resp.json()

        if result['ok']:
            return result['result']
        else:
            raise errors.Error(result['error_code'], result['description'])
