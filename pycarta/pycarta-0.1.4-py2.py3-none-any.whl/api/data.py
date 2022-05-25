from .agent import Agent
from ..base.logger import functionlogger
from ..base.typing import JsonType
from ..graph.node import Node
from numbers import Number
from typing import Union, Optional, Any

import logging


__all__ = [
    "get_sources",
    "get_resources",
    "get_data",
    "get_roots",
    "get_descendants",
    "get_ids",
    "post_graph",
    "delete_resource"
]


@functionlogger
def get_sources(agent: Agent, **kwds) -> JsonType:
    """
    Gets the names of the data sources that are accessible to the current user.

    *Note* The ability to retrieve data from these sources depends on user
    authentication to the corresponding source.

    Parameters
    ----------
    agent : pycarta.api.Agent
        The Carta agent that handles communication with the Carta server.

    Returns
    -------
    sources : list
        List of data sources to which the user has access.
    """
    response = agent.get("data", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_resources(agent: Agent, source: str, **kwds) -> JsonType:
    """
    Gets the data resources accessible through a data source. Most sources
    contain multiple resources, e.g. multiple tables in a SQL database or
    multiple datasets in HyperThought.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be found with a call to `pycarta.api.data.get_sources`.

    Returns
    -------
    resources : list
        List of resources accessible from this source.
    """
    response = agent.get(f"data/{source}", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_data(
    agent: Agent,
    source: str,
    resource: str,
    *,
    selector: str="roots",
    **kwds
):
    """
    Gets the data accessible through a data resource. Most sources
    contain multiple resources, e.g. multiple tables in a SQL database or
    multiple datasets in HyperThought.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be accessed with a call to `pycarta.api.data.get_sources`.
    resource : str
        The name of the resource to access from the source. A list of resources
        available in a source can be found by a call to
        `pycarta.api.data.get_resources`.
    selector : str
        Nodes that are to be selected. Recognized selectors can be found
        with a call to `pycarta.api.meta.get_selectors`.
    params : dict
        Parameters to control the behavior of the selector. The relevant
        parameters  can be found with a call to
        `pycarta.api.meta.get_selector_schema`.

    Returns
    -------
    graph : JSON-formatted string
        JSON-formatted representation of the graph from this source/resource
        combination.
    """
    response = agent.get(f"data/{source}/{resource}/{selector}", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_roots(
    agent: Agent,
    source: str,
    resource: str,
    **kwds
):
    """
    Gets the roots of a graph accessible through a data resource. Most sources
    contain multiple resources, e.g. multiple tables in a SQL database or
    multiple datasets in HyperThought.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be accessed with a call to `pycarta.api.data.get_data`.
    resource : str
        The name of the resource to access from the source. A list of resources
        available in a source can be found by a call to
        `pycarta.api.data.get_source`.

    Returns
    -------
    graph : JSON-formatted string
        JSON-formatted representation of the graph from this source/resource
        combination.
    """
    return get_data(agent, source, resource, selector="roots", **kwds)


@functionlogger
def get_descendants(
    agent: Agent,
    source: str,
    resource: str,
    *,
    ids: Union[str, list[str]],
    includeRoots: bool=False,
    depth: Optional[int]=1,
    traversal: str="preorder",
    **kwds
):
    """
    Gets the children vertices accessible through a data resource. Most sources
    contain multiple resources, e.g. multiple tables in a SQL database or
    multiple datasets in HyperThought.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be accessed with a call to `pycarta.api.data.get_data`.
    resource : str
        The name of the resource to access from the source. A list of resources
        available in a source can be found by a call to
        `pycarta.api.data.get_source`.
    ids : str or list of str
        The IDs whose children are to be returned.
    includeRoots : bool
        Whether to include the vertices specified by `ids` (True) or to return
        only the children (False). Default: True.
    depth : int
        The depth of descendants. 1=children; 2=children and grandchildren;
        3=children, grandchildren, and great-grandchildren; etc.
    traversal : str
        In what order to traverse the tree. Either "preorder" or "postorder".
        Default: "preorder"

    Returns
    -------
    graph : JSON-formatted string
        JSON-formatted representation of the graph from this source/resource
        combination.
    """
    params = {
        "ids": ids,
        "includeRoots": includeRoots,
        "depth": depth or "null",
        "traversal": traversal
    }
    kwds["params"] = {
        **params,
        **kwds.get("params", dict())
    }
    return get_data(agent, source, resource, selector="descendants", **kwds)

# get_children and get_descendants are synonymous
get_children = get_descendants


@functionlogger
def get_ids(
    agent: Agent,
    source: str,
    resource: str,
    *,
    ids: Union[str, list[str]],
    **kwds
):
    """
    Gets specified vertices accessible through a data resource. Most sources
    contain multiple resources, e.g. multiple tables in a SQL database or
    multiple datasets in HyperThought.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be accessed with a call to `pycarta.api.data.get_sources`.
    resource : str
        The name of the resource to access from the source. A list of resources
        available in a source can be found by a call to
        `pycarta.api.data.get_resources`.
    ids : str or list of str
        The IDs whose children are to be returned.

    Returns
    -------
    graph : JSON-formatted string
        JSON-formatted representation of the graph from this source/resource
        combination.
    """
    params = {
        "ids": ids
    }
    kwds["params"] = {
        **params,
        **kwds.get("params", dict())
    }
    return get_data(agent, source, resource, selector="include", **kwds)


# ##### POST operations ##### #
@functionlogger
def post_graph(
    agent: Agent,
    source: str,
    *,
    label: str,
    nodes: list[Node]=[],
    edges: list[tuple[Node, Node]]=[],
    directed: bool=True,
    **kwds
):
    """
    Posts a graph to Carta.

    A graph must have a label and either a list of nodes, a list of edges
    as tuple (from, to), or both. The nodes in the graph are the set of
    all unique nodes in either of these lists.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be accessed with a call to `pycarta.api.data.get_sources`.
    label : str
        The label for the graph.
    nodes : list[Node]
        List of nodes in the graph. Either a list of nodes may be provided,
        a list of edges (see edges), or both.
    edges : list[tuple[Node, Node]]
        List of edges, where each edge is a tuple of edges, (from, to), that
        describe the edge from `from` node to `to` node.
    directed : bool
        Whether the graph directed (True) or undirected (False).
    **kwds : dict
        Other options/keywords will be passed to POST.

    Returns
    -------
    `requests.Response`
        The response from the Carta server. Generally this should be checked
        to verify the success (or failure) of the call, e.g.

            nodes = [...] # list of nodes
            edges = [...] # list of edges
            response = post_graph(
                agent,
                "user",
                label="My Graph",
                nodes=nodes,
                edges=edges
            )
            if response:
                print("Graph was posted successfully.")
            else:
                print("Graph was not posted.")
    """
    logger = logging.getLogger()
    nodeSet = set(nodes)
    for a, b in edges:
        nodeSet.add(a)
        nodeSet.add(b)
    # Format the nodes and edges in vnd.vis+json format.
    logger.debug("Formatting nodes and edges in vnd.vis+json format.")
    graph = {
        "label": label,
        "directed": directed,
        "dynamic": True,
        "nodes": [n.json() for n in nodeSet],
        "edges": [
            {
                "id": f"{a.id}->{b.id}",
                "from": a.id,
                "to": b.id
            }
            for a, b in edges
        ]
    }
    response = agent.post(
        f"data/{source}",
        json=graph,
        **kwds
    )
    if response:
        return response.json()
    else:
        logging.info(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        # raise IOError(f"{__name__} API request failed with "
        #               f"error status code {response.status_code}")
        return response
        # return None


# ##### DELETE operations ##### #
@functionlogger
def delete_resource(
    agent: Agent,
    source: str,
    resource: str,
    **kwds
):
    """
    Posts a graph to Carta.

    A graph must have a label and either a list of nodes, a list of edges
    as tuple (from, to), or both. The nodes in the graph are the set of
    all unique nodes in either of these lists.

    Parameters
    ----------
    agent : pycarta.api.Agent
        Handles communication with the Carta server.
    source : str
        The name of the source to be accessed. A list of available sources
        can be accessed with a call to `pycarta.api.data.get_sources`.
    resource : str
        The resource identifier of the resource to be deleted.
    **kwds : dict
        Other options/keywords will be passed to POST.

    Returns
    -------
    `requests.Response`
        The response from the Carta server. Generally this should be checked
        to verify the success (or failure) of the call, e.g.

            response = post_graph(
                agent,
                "user",
                "0"
            )
            if response:
                print("Graph was deleted successfully.")
            else:
                priint("Graph was not deleted.")
    """
    return agent.delete(f"data/{source}/{resource}", **kwds)
