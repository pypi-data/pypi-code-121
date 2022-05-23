"""HTTP client for TrustedTwin API client"""
import json
import logging
from typing import Dict, Optional, Any

import requests
from requests import Response

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import TTResponse

logger = logging.getLogger("trusted_twin")


class HTTPClient:
    """HTTP client used by TrustedTwin Service"""

    def __init__(self, host_name: str, auth: Optional[str] = None):
        """Initialize object.

        :param auth: authorization token
        :param host_name: string containing host name
        """
        self.host_name = host_name
        self.headers = {"Content-Type": "application/json"}
        if auth:
            self.headers["Authorization"] = auth
        else:
            logger.warning("Auth token not set")

    def __repr__(self) -> str:
        """Return nicer print presentation."""
        return "{} - {}".format(self.__class__.__name__, self.host_name)

    @staticmethod
    def _call(
        method: RESTMethod,
        url: str,
        headers: Optional[Dict] = None,
        body: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs: Any
    ) -> Response:
        """Perform actual call to API

        :param method: REST API method to be executed on an endpoint e.g. 'GET', 'POST', 'PATCH'
        :param url: url to be called
        :param headers: headers for request
        :param body: optional payload passed as a json object
        :param params: optional parameters passed as key-worded arguments
        :return: endpoint response
        """
        req_method = getattr(requests, str(method).lower())

        logging.debug("Calling url: %s", url)

        return req_method(
            url=url,
            data=json.dumps(body) if body else None,
            headers=headers,
            params=params,
            **kwargs
        )

    def execute_request(
        self,
        method: RESTMethod,
        url_root: str,
        endpoint: str,
        body: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs: Any
    ) -> TTResponse:
        """Execute API request"""
        url = "{}/{}".format(url_root, endpoint)
        params = (
            {key: value for key, value in params.items() if value is not None}
            if params
            else {}
        )

        response = self._call(
            method=method,
            url=url,
            body=body,
            params=params,
            headers=self.headers,
            **kwargs
        )

        return TTResponse(body=response.text, http_code=response.status_code)
