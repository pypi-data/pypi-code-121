"""
Module to get graphedges data
"""
from typing import List
from deeplabel.basemodel import DeeplabelBase
import deeplabel.client
from deeplabel.exceptions import InvalidIdError


class GraphEdge(DeeplabelBase):
    graph_id: str
    graph_edge_id: str
    src_graph_node_id: str
    target_graph_node_id: str

    @classmethod
    def _from_search_params(cls, params: str, client: "deeplabel.client.BaseClient") -> List["GraphEdge"]:  # type: ignore Used to ignore using private class BaseClient
        """Private classmethod used internally by other classmethods to fetch
        graphNodes

        Returns:
            List[GraphEdge]: Returns a List of GraphEdge or an empty list of
            the query params don't match anything
        """
        resp = client.get("/graphs/edges", params=params)
        edges = resp.json()["data"]["graphEdges"]
        edges = [cls(**edge, client=client) for edge in edges]
        return edges

    @classmethod
    def from_graph_edge_id(cls, graph_edge_id: str, client: "deeplabel.client.BaseClient") -> "GraphEdge":  # type: ignore Used to ignore using private class BaseClient
        edges = cls._from_search_params({"graphEdgeId": graph_edge_id}, client)
        if not len(edges):
            raise InvalidIdError(
                f"No Graph Edges found for graphEdgeId {graph_edge_id}"
            )
        # Since edge_id will always yield atmax 1 edge
        return edges[0]

    @classmethod
    def from_target_node_id(cls, target_graph_node_id: str, client: "deeplabel.client.BaseClient") -> List["GraphEdge"]:  # type: ignore
        """Fetch all GraphEdge that point to given target_graph_node_id

        Returns:
            List[GraphEdge]: List of graph edges reaching the given
            target_graph_node_id. Would return empty list for head nodes
        """

        edges = cls._from_search_params(
            params={"targetGraphNodeId": target_graph_node_id}, client=client
        )
        return edges

    @classmethod
    def from_src_node_id(cls, src_graph_node_id: str, client: "deeplabel.client.BaseClient") -> List["GraphEdge"]:  # type: ignore
        """Fetch all GraphEdge that start from given src_graph_node_id

        Returns:
            List[GraphEdge]: List of graph edges starting from the given
            src_graph_node_id. Would return empty list for leaf nodes
        """

        edges = cls._from_search_params(
            params={"srcGraphNodeId": src_graph_node_id}, client=client
        )
        return edges
