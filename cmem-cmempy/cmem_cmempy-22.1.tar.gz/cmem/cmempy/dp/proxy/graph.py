"""API for managing graphs in DP."""

import os
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from requests.exceptions import HTTPError

from cmem.cmempy import config
from cmem.cmempy.api import (
    get_json,
    request
)


def get_graph_uri_pattern():
    """Get endpoint URI pattern for a graph (graph store protocol)."""
    return config.get_dp_api_endpoint() + "/proxy/{}/graph?graph={}"


def _get_graph_uri(endpoint_id, graph):
    escaped_graph = quote(graph)
    return get_graph_uri_pattern().format(endpoint_id, escaped_graph)


def get(
        graph,
        endpoint_id="default",
        owl_imports_resolution=False,
        accept="application/n-triples",
        stream=False
):
    """GET graph.

    per default, graphs are exported without imported graphs.

    Args:
        graph (str): The URI of the requested graph.
        endpoint_id (str): Optional endpoint ID (always 'default').
        owl_imports_resolution: Optional request imported graph as well.
        accept: Optional mimetype to request.
        stream: Enable streaming on the response object.

    Returns:
        requests.Response object
    """
    headers = {"Accept": accept}
    uri = _get_graph_uri(endpoint_id, graph) \
        + "&owlImportsResolution=" \
        + str(owl_imports_resolution).lower()
    return request(
        uri,
        method="GET",
        headers=headers,
        stream=stream
    )


def get_streamed(
        graph,
        endpoint_id="default",
        owl_imports_resolution=False,
        accept="application/n-triples"
):
    """GET graph (streamed).

    same as get

    Args:
        graph (str): The URI of the requested graph.
        endpoint_id (str): Optional endpoint ID (always 'default').
        owl_imports_resolution: Optional request imported graph as well.
        accept: Optional mimetype to request.

    Returns:
        requests.Response object
    """
    return get(
        graph,
        endpoint_id=endpoint_id,
        owl_imports_resolution=owl_imports_resolution,
        accept=accept
    )


def delete(
        graph,
        endpoint_id="default"):
    """DELETE graph."""
    uri = _get_graph_uri(endpoint_id, graph)
    return request(
        uri,
        method="DELETE"
    )


def post(
        graph,
        file,
        endpoint_id="default",
        replace=False):
    """Upload graph.

    Add the content of triple to a remote graph or replace the remote graph
    with the content of a triple file.

    Args:
        graph (str): The URI of the remote graph.
        file: The triple file
        endpoint_id (str): Optional endpoint ID (always 'default').
        replace (bool): add (False) or replace (True)

    Returns:
        requests.Response object

    """
    uri = _get_graph_uri(endpoint_id, graph) \
        + "&replace=" \
        + str(replace).lower()
    with open(file, 'rb') as file_handle:
        return request(
            uri,
            method="POST",
            files={'file': (os.path.basename(file), file_handle)}
        )


def post_streamed(
        graph,
        file,
        endpoint_id="default",
        replace=False,
        content_type="text/turtle"
):
    """Upload graph (streamed).

    Add the content of triple to a remote graph or replace the remote graph
    with the content of a triple file.

    Args:
        graph (str): The URI of the remote graph.
        file: The triple file
        endpoint_id (str): Optional endpoint ID (always 'default').
        replace (bool): add (False) or replace (True)
        content_type (str): mime type of the file to post (default is turtle)

    Returns:
        requests.Response object

    """
    uri = _get_graph_uri(endpoint_id, graph) \
        + "&replace=" \
        + str(replace).lower()
    headers = {"Content-Type": content_type}
    # https://2.python-requests.org/en/master/user/advanced/#streaming-uploads
    with open(file, 'rb') as opened_file:
        response = request(
            uri,
            method="POST",
            headers=headers,
            data=opened_file
        )
    return response


def put(
        graph,
        rdf_data,
        rdf_serialization,
        endpoint_id="default"):
    """PUT graph."""
    headers = {"Content-Type": rdf_serialization}
    uri = _get_graph_uri(endpoint_id, graph)
    return request(
        uri,
        method="PUT",
        data=rdf_data,
        headers=headers
    )


def get_graphs_list():
    """Get a list of graph descriptions the user is allowed to access.

    Returns:
        parsed json response
    Examples
        {
        "assignedClasses": [
            "http://rdfs.org/ns/void#Dataset"
        ],
        "diProjectGraph": false,
        "graphProperies": [
            "https://vocab.eccenca.com/shui/isSystemResource"
        ],
        "iri": "https://ns.eccenca.com/data/queries/",
        "label": {
            "fromIri": false,
            "graph": "https://ns.eccenca.com/data/queries/",
            "iri": "https://ns.eccenca.com/data/queries/",
            "lang": "en",
            "title": "CMEM Query Catalog",
            "when": "16:35:40.353"
        },
        "projectInternal": false,
        "systemResource": true,
        "writeable": true
    }
    """
    endpoint = config.get_dp_api_endpoint() + "/graphs/list"
    return get_json(endpoint)


def get_graph_imports(graph):
    """Get the list of graphs, which a graph imports, resolved transitively.

    Args:
        graph (str): The IRI of the graph

    Returns:
        list of graph IRIs which this graph imports
    """
    endpoint = config.get_dp_api_endpoint() + "/graphs/imports"
    params = {
        "graph": graph
    }
    return get_json(endpoint, params=params)


def get_graph_import_tree(graph):
    """Get the graph imported graphs, which this graph includes.

    Args:
        graph (str): The IRI of the graph

    Returns:
        structure of graph IRIs which this graph imports
    """
    endpoint = config.get_dp_api_endpoint() + "/graphs/importTree"
    params = {
        "graph": graph
    }
    try:
        response = get_json(endpoint, params=params)
    except HTTPError:
        return {graph: []}
    if response == {}:
        return {graph: []}
    return get_json(endpoint, params=params)
