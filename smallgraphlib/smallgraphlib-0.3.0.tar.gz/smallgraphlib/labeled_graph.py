from abc import ABC
from itertools import chain
from numbers import Real
from typing import Iterable, Tuple, Dict, List, TypeVar, Generic

from smallgraphlib.graph import Graph, Node, UndirectedEdge, Edge, AbstractGraph, DirectedGraph
from math import inf

Label = TypeVar("Label")
LabeledEdge = Tuple[Node, Node, Label]
WeightedEdge = Tuple[Node, Node, float]


class AbstractLabeledGraph(AbstractGraph, ABC, Generic[Label]):
    def __init__(
            self,
            nodes: Iterable[Node],
            *labeled_edges: LabeledEdge,
            sort_nodes: bool = True,
    ):
        edges: List[Edge] = []
        self.labels: Dict[UndirectedEdge, List[Label]] = {}
        for *edge, label in labeled_edges:
            edges.append(edge)  # type: ignore
            self.labels.setdefault(frozenset(edge), []).append(label)

        super().__init__(nodes, *edges, sort_nodes=sort_nodes)

    @classmethod
    def from_dict(cls, edge_label_dict: dict = None, /, **edge_label):
        """LabeledUndirectedGraph.from_dict(AB=1, AC=3, BC=4)"""
        if edge_label_dict is None:
            edge_label_dict = {}
        edge_label_dict.update(edge_label)
        nodes = set(chain(*(edge for edge in edge_label_dict)))
        return cls(nodes, *((*edge, label) for edge, label in edge_label_dict.items()))  # type: ignore


class LabeledGraph(AbstractLabeledGraph, Graph):
    pass


class LabeledDirectedGraph(AbstractLabeledGraph, DirectedGraph):
    pass


class AbstractWeightedGraph(AbstractLabeledGraph, ABC):
    def __init__(
            self,
            nodes: Iterable[Node],
            *weighted_edges: WeightedEdge,
            sort_nodes: bool = True,
    ):
        super().__init__(nodes, *weighted_edges, sort_nodes=sort_nodes)
        self.weights: Dict[Edge, List[float]] = self.labels  # type: ignore
        for weights in self.weights.values():
            for weight in weights:
                if not isinstance(weight, Real):
                    raise ValueError(f"Edge weight {weight!r} is not a real number.")

    def weight(self, node1, node2) -> float:
        return min(self.weights[self._edge(node1, node2)], default=inf)


class WeightedGraph(AbstractWeightedGraph, LabeledGraph):
    pass


class WeightedDirectedGraph(AbstractWeightedGraph, LabeledDirectedGraph):
    pass
