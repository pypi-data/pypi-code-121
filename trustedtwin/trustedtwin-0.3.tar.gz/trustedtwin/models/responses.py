"""Response models for API client"""
import json
from typing import Dict, Any

from trustedtwin.exceptions import get_tt_exception


class TTResponse:
    """Wrapper for TT API response"""

    def __init__(self, body: str, http_code: int):
        """Initialize object"""
        self._body = body
        self.http_code = http_code

    @property
    def body(self) -> Dict:
        """Return body loaded from json"""
        return json.loads(self._body)


def process_response(resp: TTResponse, api_operation: str, **kwargs: Any) -> Dict:
    """Handle response returned from API"""
    raise_on_error = kwargs.get("raise_on_error", True)

    if not raise_on_error:
        return {"http_code": resp.http_code, "body": resp.body}

    if resp.http_code < 400:
        return resp.body

    raise get_tt_exception(resp, api_operation)
