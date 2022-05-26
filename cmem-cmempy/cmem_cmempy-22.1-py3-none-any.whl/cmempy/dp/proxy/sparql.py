"""API for running SPARQL queries on DP proxy endpoints."""

from base64 import b64encode

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_query_api_endpoint():
    """Get endpoint URI pattern for a SPARQL query endpoint."""
    return config.get_dp_api_endpoint() + "/proxy/{}/sparql"


# pylint: disable-msg=too-many-arguments
def get(
        query,
        endpoint_id="default",
        owl_imports_resolution=True,
        accept="application/sparql-results+json",
        named_graph_uri=(),
        default_graph_uri=(),
        base64_encoded=False,
        cd_target=None
):
    """GET query results.

    Args:
        query (str): The SPARQL query.
        endpoint_id: The DataPlatform endpoint ID
        owl_imports_resolution (bool): turn on owl:imports resolution,
            which means if a graph imports a second graph, the data of
            the second graph is included when querying the first graph
        accept (str): mime type, which content is accepted
        named_graph_uri (list): list of GRAPH URIs
        default_graph_uri (list):  list of GRAPH URIs
        base64_encoded (bool): flag to turn on base64 encoding of the request
        cd_target (str or None): Which name has the downloaded file?
    """
    headers = {"Accept": accept}
    uri = get_query_api_endpoint().format(endpoint_id)
    params = {}
    if base64_encoded:
        params["query"] = b64encode(query.encode())
        params["base64encoded"] = "true"
    else:
        params["query"] = query
    if cd_target:
        params["cdTarget"] = cd_target
    if len(named_graph_uri) > 0:
        params["named-graph-uri"] = named_graph_uri
    if len(default_graph_uri) > 0:
        params["default-graph-uri"] = default_graph_uri
    if not owl_imports_resolution:
        # default of owl_imports_resolution is true, so only add on false
        params["owlImportsResolution"] = "false"
    return send_request(
        uri, method="GET", headers=headers, params=params
    ).decode("utf-8")


def post(
        query,
        endpoint_id="default",
        owl_imports_resolution=True,
        accept="application/sparql-results+json",
        named_graph_uri=(),
        default_graph_uri=(),
        base64_encoded=False,
        cd_target=None,
        distinct=False,
        limit=None,
        offset=None,
        timeout=None
):
    """Get query results via POST request (recommended).

    Args:
        query (str): The SPARQL query.
        endpoint_id: The DataPlatform endpoint ID
        owl_imports_resolution (bool): turn on owl:imports resolution,
            which means if a graph imports a second graph, the data of
            the second graph is included when querying the first graph
        accept (str): mime type, which content is accepted
        named_graph_uri (list): list of GRAPH URIs
        default_graph_uri (list):  list of GRAPH URIs
        base64_encoded (bool): flag to turn on base64 encoding of the request
        cd_target (str or None): Which name has the downloaded file?
        distinct (bool): query override - turn on DISTINCT SELECT
        limit (int or None): query override - set SELECT LIMIT
        offset (int or None): query override - set SELECT OFFSET
        timeout (int or None): timeout in milliseconds
    """
    headers = {"Accept": accept}
    uri = get_query_api_endpoint().format(endpoint_id)
    data = {}
    if base64_encoded:
        data["query"] = b64encode(query.encode())
        data["base64encoded"] = "true"
    else:
        data["query"] = query
    if cd_target:
        data["cdTarget"] = cd_target
    if len(named_graph_uri) > 0:
        data["named-graph-uri"] = named_graph_uri
    if len(default_graph_uri) > 0:
        data["default-graph-uri"] = default_graph_uri
    if not owl_imports_resolution:
        # default of owl_imports_resolution is true, so only add on false
        data["owlImportsResolution"] = "false"
    if distinct:
        data["distinct"] = "true"
    if limit:
        data["limit"] = limit
    if offset:
        data["offset"] = offset
    if timeout:
        data["timeout"] = timeout
    return send_request(
        uri, method="POST", headers=headers, data=data
    ).decode("utf-8")
