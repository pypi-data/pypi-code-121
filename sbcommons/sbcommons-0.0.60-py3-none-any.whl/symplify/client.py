from time import sleep
from typing import Dict

import requests
from requests.adapters import HTTPAdapter
from sbcommons.logging.lambda_logger import get_logger
from urllib3 import Retry

logger = get_logger('symplify_client')


class SymplifyClient:
    rate_limit = 60

    def __init__(self, token: str, customer_id: int, list_id: int = None,
                 delimiter: str = '|'):
        self.token = token
        self.customer_id = customer_id
        self.list_id = list_id
        self.delimiter = delimiter

    def __enter__(self):
        session = requests.session()
        session.mount('https://', self._retry_adapter(retries=3, backoff_factor=4))
        session.headers = self._build_base_header()
        self.session = session
        return self

    def __exit__(self, *_):
        self.session.close()

    def create_import(self, import_type: str = 'ADD'):
        url = self._build_url(f'lists/{self.list_id}/imports')
        payload = {
            'delimiter': f'{ord(self.delimiter)}',
            'encoding': 'UTF8',
            'type': import_type,
            'identityColumn': 'originalId'
        }
        self.session.headers['Content-Type'] = 'application/json'
        return self._request('POST', url, json=payload).json()['id']

    def post_list(self, import_id: str, list_data: bytes):
        url = self._build_url(f'lists/{self.list_id}/recipients/{import_id}')
        self.session.headers['Content-Type'] = 'text/csv'
        return self._request('POST', url, data=list_data).json()['batchId']

    def check_batch(self, batch_id: int):
        url = self._build_url(f'batches/{batch_id}')
        self.session.headers['Content-Type'] = 'application/json'
        return self._request('GET', url).json()

    def _build_base_header(self) -> Dict:
        return {
            'Accept': 'application/json',
            'X-Carma-Authentication-Token': self.token
        }

    def _build_url(self, endpoint):
        return f'http://www.carmamail.com:80/rest/{self.customer_id}/{endpoint}'

    def _request(self, method: str = 'GET', url: str = None, *args, **kwargs):
        response = self.session.request(method, url, *args, **kwargs)
        if response.status_code == 429:
            # rate limited (should be one request per minute according to weird error msg).
            logger.info(f'Rate limited by the Symplify API. Sleeping for {self.rate_limit} seconds')
            sleep(self.rate_limit)
            return self.session.request(method, url, *args, **kwargs)
        return response

    @staticmethod
    def _retry_adapter(
            retries=5,
            backoff_factor=1.0,
            status_forcelist=(500, 501, 502, 503, 504)
    ):
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        return HTTPAdapter(max_retries=retry)
