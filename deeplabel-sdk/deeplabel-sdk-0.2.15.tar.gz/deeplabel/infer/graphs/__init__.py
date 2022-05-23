from typing import Dict, List
import deeplabel.client
import deeplabel
from deeplabel.exceptions import InvalidIdError
import deeplabel.infer.graphs.graph_nodes as graph_nodes
import deeplabel.infer.graphs.graph_edges as graph_edges
from deeplabel.basemodel import DeeplabelBase


class Graph(DeeplabelBase):
    graph_id: str
    name: str
    project_id: str

    @classmethod
    def from_search_params(
        cls, params: Dict[str, str], client: "deeplabel.client.BaseClient"
    ) -> List["Graph"]:
        resp = client.get("/graphs", params=params)
        graphs = resp.json()["data"]["graphs"]
        return [cls(**graph, client=client) for graph in graphs]

    @classmethod
    def from_graph_id(cls, graph_id: str, client: "deeplabel.client.BaseClient") -> "Graph":  # type: ignore Used to ignore using private class BaseClient
        graphs = cls.from_search_params(params={"graphId": graph_id}, client=client)
        if not len(graphs):
            raise InvalidIdError(f"No Graph found for graphId {graph_id}")
        return graphs[0]

    @property
    def nodes(self) -> List["graph_nodes.GraphNode"]:
        if hasattr(self, "_nodes"):
            return self._nodes  # type: ignore
        assert hasattr(self, "client"), (
            f"Nodes property can only be accessed for fetched "
            "Graph objects that have graph.client access."
        )
        nodes = graph_nodes.GraphNode._from_search_params(
            {"graphId": self.graph_id, "limit": "-1", "project_id": self.project_id},
            client=self.client,
        )
        return nodes

    @property
    def edges(self) -> List["graph_edges.GraphEdge"]:
        if hasattr(self, "_edges"):
            return self._edges  # type: ignore
        assert hasattr(self, "client"), (
            "edges property can only be accessed for fetched "
            "Graph objects that have graph.client access."
        )
        edges = graph_edges.GraphEdge._from_search_params(
            {"graphId": self.graph_id, "limit": "-1", "project_id": self.project_id},
            client=self.client,
        )
        return edges
