"""
Lesson -> Assignment -> Exercise -> Result
"""
from __future__ import annotations
import logging
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class CollectorClient:
    def __init__(
        self,
        url,
        auth,
        ignore_errors: bool = True,
        headers: dict = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        },
    ) -> None:
        self.url = url
        self.auth = HTTPBasicAuth(auth.get('username'), auth.get('token'))
        self.ignore_errors = ignore_errors
        self.headers = headers
        if self.ignore_errors:
            logger.warn(
                'ignoring all request errors and continuing without stack trace.'
            )

    def _join_url_path(self, path):
        return '/'.join(s.strip('/') for s in [self.url, path])

    def _make_request(self, func, *args, **kwargs):
        headers = kwargs.pop('headers', self.headers)
        result = func(*args, **kwargs, headers=headers)
        try:
            result.raise_for_status()
            result = result.json()
        except Exception as e:
            logger.warn(result.json())
            logger.error(e)
            if not self.ignore_errors:
                raise
        return result

    def get(self, *args, url_path, **kwargs):
        return self._make_request(
            requests.get,
            url=self._join_url_path(url_path),
            auth=self.auth,
            *args,
            **kwargs,
        )

    def put(self, *args, url_path, **kwargs):
        return self._make_request(
            requests.put,
            url=self._join_url_path(url_path),
            auth=self.auth,
            *args,
            **kwargs,
        )

    def post(self, *args, url_path, **kwargs):
        return self._make_request(
            requests.post,
            url=self._join_url_path(url_path),
            auth=self.auth,
            *args,
            **kwargs,
        )

    def delete(self, *args, url_path, **kwargs):
        return self._make_request(
            requests.delete,
            url=self._join_url_path(url_path),
            auth=self.auth,
            *args,
            **kwargs,
        )
