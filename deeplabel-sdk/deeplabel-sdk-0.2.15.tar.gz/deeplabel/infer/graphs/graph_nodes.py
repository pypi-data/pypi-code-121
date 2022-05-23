from enum import Enum
from typing import Any, Dict, List, Optional
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.basemodel import DeeplabelBase
import deeplabel.infer.graphs
import deeplabel.infer.graphs.graph_edges as graph_edges


class GraphNodeTypes(Enum):
    DLMODEL = "DLMODEL"  # deprecated
    SCRIPT = "SCRIPT"  # deprecated
    NOTEBOOK = "NOTEBOOK"
    VIDEOWRITE = "VIDEOWRITE"
    VIDEO_CONVERSION = "VIDEO_CONVERSION"


class GraphNode(DeeplabelBase):
    graph_node_id: str
    name: str
    notebook_id: str
    type: GraphNodeTypes
    dl_model_id:Optional[str]
    is_head: bool
    is_shown: bool
    graph_id: str

    @classmethod
    def _from_search_params(cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient") -> List["GraphNode"]:  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/graphs/nodes", params=params)
        nodes = resp.json()["data"]["graphNodes"]
        nodes = [cls(**node, client=client) for node in nodes]
        return nodes

    @classmethod
    def from_graph_node_id(cls, graph_node_id: str, client: "deeplabel.client.BaseClient") -> "GraphNode":  # type: ignore Used to ignore using private class BaseClient
        nodes = cls._from_search_params({"graphNodeId": graph_node_id}, client)
        if not len(nodes):
            raise InvalidIdError(f"No Graph Node found for graphNodeId {graph_node_id}")
        # Since node_id will always yield 1 graphNode, return that instead of a list
        return nodes[0]

    @property
    def graph(self) -> "deeplabel.infer.graphs.Graph":
        graph = deeplabel.infer.graphs.Graph.from_graph_id(
            self.graph_id, self.client
        )
        return graph

    @property
    def prev_nodes(self):
        incoming_edges = graph_edges.GraphEdge.from_target_node_id(self.graph_node_id, self.client)
        # mapping between graph_node_id and the corresponding node objects
        memo = {node.graph_node_id: node for node in self.graph.nodes}
        prev_nodes = [
            memo[edge.src_graph_node_id]
            for edge in incoming_edges
        ]
        return prev_nodes

    @property
    def next_nodes(self):
        outgoing_edges = graph_edges.GraphEdge.from_src_node_id(self.graph_node_id, self.client)
        # mapping between graph_node_id and the corresponding node objects
        memo = {node.graph_node_id: node for node in self.graph.nodes}
        next_nodes = [
            memo[edge.target_graph_node_id]
            for edge in outgoing_edges
        ]
        return next_nodes
