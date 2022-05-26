from datetime import datetime
from types import SimpleNamespace
from typing import Dict
from typing import List

import requests
from freshdesk.models.api import APIVersion
from freshdesk.models.plan import Plan
from freshdesk.store import LimitInfo
from requests.models import Response


class Client:

    """Represents a Freshdesk client to interacto with their REST API.

    Specifically this is for the 2nd Version of their API.
    """

    api = SimpleNamespace()

    def __init__(
        self,
        domain: str,
        api_key: str,
        plan: Plan = Plan.BLOSSOM,
        version: APIVersion = APIVersion(2),
    ):

        self.domain = domain
        self.api_key = api_key
        self.plan = plan
        self.version = version

        self.history: List[Response] = []
        self.limits: List[LimitInfo] = []

    @property
    def hostname(self) -> str:
        return f"https://{self.domain}.freshdesk.com"

    @property
    def base_url(self) -> str:
        return self.hostname + self._api_route + self.version.path

    @property
    def _api_route(self) -> str:
        return "/api"

    def _request(self, url: str, method: str = "GET", **kwargs):
        """All HTTP requests are made through this method."""

        response = requests.request(
            method=method,
            url=url,
            auth=(self.api_key, "dummy"),
            **kwargs,  # type: ignore
        )
        self.history.append(response)
        self._parse_response(response)  # Limits, Pagination, Resource Location
        self._rate_limit_check()  # Check if we need to wait, etc.

        return response

    def _rate_limit_check(self) -> None:
        """Check if we're below this app's rate limit threshold."""
        # Unimplemented

    @staticmethod
    def _get_limit_info(headers) -> Dict[str, int]:

        calls_per_minute = int(headers.get("X-RateLimit-Total", 0))
        calls_remaining = int(headers.get("X-RateLimit-Remaining", 0))
        calls_consumed = int(headers.get("X-RateLimit-Used-CurrentRequest", 0))
        retry_time = int(headers.get("Retry-After", 0))  # seconds

        return dict(
            calls_per_minute=calls_per_minute,
            calls_remaining=calls_remaining,
            calls_consumed=calls_consumed,
            retry_time=retry_time,
        )

    def _parse_response(self, response: requests.Response):
        """Parse response and update self.

        * Limit Information
        * Pagination
        * Resource Location
        """

        headers = response.headers

        # Limit Information
        limit_info: Dict[str, int] = self._get_limit_info(headers)
        limits: LimitInfo = LimitInfo(
            datetime=datetime.now().astimezone(),
            calls_per_minute=limit_info["calls_per_minute"],
            calls_remaining=limit_info["calls_remaining"],
            calls_consumed=limit_info["calls_consumed"],
            retry_time=limit_info["retry_time"],
        )

        # Store Limits
        self.limits.append(limits)
        # TODO: Add LimitStore
        # store.insert(limits)

        # Pagination, if applicable
        # The 'link' header in the response will hold the next page url if
        # exists. If you have reached the last page of objects, then the link
        # header will not be set.
        pagination_link = headers.get("link", "")
        self.pagination_link = pagination_link  # Hotfix to add this to model

        # Location Header:
        # POST requests will contain the Location Header in the response that
        # points to the URL of the created resource.
        # Response
        # HTTP STATUS: HTTP 201 Created
        # Headers:
        # "Location": https://domain.freshdesk.com/api/v2/tickets/1
        resource_location = headers.get("Location", "")
        self.resource_location = (
            resource_location  # Hotfix to add this to model  # noqa: 501
        )
