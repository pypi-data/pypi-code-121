"""API for eccenca DataPlatform Label Resolution."""

import json

from cmem.cmempy import config
from cmem.cmempy.api import request


def resolve(iris, graph=None):
    """Resolve IRIs to short form labels.

    If none can be found in the data, the iri itself is used to create one.

    Possible extension: langPrefs parameter

    Args:
        iris: The list of iris to resolve.
        graph: The context/graph, in which the lookup should take place.

    Raises:
        ValueError
    """
    uri = config.get_dp_api_endpoint() + "/api/explore/titles"

    if not isinstance(iris, list):
        raise ValueError(
            "Parameter 'iris' has to be a list of (iri) strings."
        )

    data = json.dumps(iris)
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json"
    }

    params = {}
    if graph is not None:
        params["contextGraph"] = graph

    response = json.loads(request(
        uri,
        method="POST",
        headers=headers,
        params=params,
        data=data
    ).content)
    return response
