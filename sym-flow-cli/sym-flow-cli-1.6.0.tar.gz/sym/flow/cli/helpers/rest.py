import json
import uuid
from typing import Literal, Optional

import requests
from requests.exceptions import SSLError

from sym.flow.cli.errors import (
    NotAuthorizedError,
    SymAPIAggregateError,
    SymAPIMissingEntityError,
    SymAPIRequestError,
    SymAPIUnknownError,
)

MethodT = Literal["GET", "HEAD", "PATCH", "POST", "PUT", "DELETE"]


class SymRESTClient:
    """Basic HTTP client for the Sym API."""

    last_request_id: str

    def __init__(self, url: str, access_token: Optional[str]):
        self.base_url = url
        self.access_token = access_token
        self.last_request_id = None  # type: ignore

    def make_headers(self, force_auth: bool = True) -> dict:
        if force_auth and not self.access_token:
            raise NotAuthorizedError()

        request_id = self.last_request_id = str(uuid.uuid4())
        headers = {
            "X-Sym-Request-ID": request_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return headers

    def handle_response(
        self,
        response: requests.Response,
        *,
        validate: bool = True,
    ) -> requests.Response:
        """Validate a response from the server and raise, or return the response."""
        if not validate:
            return response

        if response.ok:
            try:
                response.json()
            except json.decoder.JSONDecodeError as err:
                raise SymAPIRequestError(
                    "The Sym API returned a malformed response.",
                    request_id=self.last_request_id,
                ) from err
            else:
                return response

        try:
            details = response.json()
            if error := details.get("message"):
                raise SymAPIAggregateError(error, self.last_request_id)
            elif errors := details.get("errors"):
                raise SymAPIAggregateError(errors, self.last_request_id)
            elif error := details.get("error"):
                raise SymAPIAggregateError(error, self.last_request_id)
            else:
                raise SymAPIUnknownError(
                    response_code=response.status_code,
                    request_id=self.last_request_id,
                )
        except (ValueError, KeyError):
            raise SymAPIUnknownError(
                response_code=response.status_code,
                request_id=self.last_request_id,
            )

    def _request(
        self,
        method: MethodT,
        endpoint: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        validate: bool = True,
        force_auth: bool = True,
    ) -> requests.Response:
        try:
            response = requests.request(
                method,
                url=f"{self.base_url}/{endpoint}",
                params=params or {},
                data=json.dumps(data) if data else None,
                headers=self.make_headers(force_auth=force_auth),
            )
        except SSLError as err:
            raise SymAPIUnknownError(
                response_code=0, request_id=self.last_request_id
            ) from err

        return self.handle_response(response, validate=validate)

    def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        *,
        validate: bool = True,
        force_auth: bool = True,
    ) -> requests.Response:
        return self._request(
            "GET", endpoint, params=params, validate=validate, force_auth=force_auth
        )

    def delete(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        return self._request("DELETE", endpoint, params=params)

    def head(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        return self._request("HEAD", endpoint, params=params)

    def patch(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        return self._request("PATCH", endpoint, data=data)

    def post(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        return self._request("PUT", endpoint, data=data)
