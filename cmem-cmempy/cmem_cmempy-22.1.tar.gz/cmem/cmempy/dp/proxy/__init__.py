"""API for DP /proxy/{} endpoint."""

import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get(endpoint_id="default"):
    """Retrieve list of graphs from DP endpoint."""
    proxy_uri = config.get_dp_api_endpoint() + "/proxy/{}"
    return json.loads(send_request(
        proxy_uri.format(
            endpoint_id
        ),
        method="GET"
    ).decode("utf-8"))
