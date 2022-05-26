"""API for running SPARQL queries on DP proxy endpoints."""

from base64 import b64encode

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_update_endpoint():
    """Get endpoint URI pattern for a SPARQL update endpoint."""
    return config.get_dp_api_endpoint() + "/proxy/{}/update"


# pylint: disable-msg=too-many-arguments
def post(query,
         endpoint_id="default",
         accept="application/sparql-update",
         named_graph_uri=(),
         default_graph_uri=(),
         base64_encoded=False
         ):
    """POST update / insert query."""
    headers = {"Accept": accept}
    uri = get_update_endpoint().format(endpoint_id)

    if base64_encoded:
        query = b64encode(query.encode())
        data = {'update': query, 'base64encoded': 'true'}
    else:
        data = {'update': query}

    if named_graph_uri:
        data['named-graph-uri'] = []
        for graph in named_graph_uri:
            data['named-graph-uri'].append(graph)

    if default_graph_uri:
        data['default-graph-uri'] = []
        for graph in default_graph_uri:
            data['default-graph-uri'].append(graph)

    response = send_request(
        uri=uri,
        method="POST",
        data=data,
        headers=headers
    )
    return response.decode("utf-8")
