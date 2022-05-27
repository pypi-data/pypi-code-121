from typing import Optional, Any, List

from tokyo_annotation.utils import Map

class DirectedGraph:
    def __init__(
        self,
        nodes: Optional[Map] = None
    ):
        self.nodes = nodes if nodes else Map()
        self.dimension = self.nodes.counter
        self.edges = self.init_edges(self.dimension)

    def init_edges(
        self,
        dimension: int):
        return [0 for i in range(0, dimension ** 2)]

    def get_index(
        self,
        x: int,
        y: int,
        dimension: Optional[int] = None):
        dimension = dimension if dimension else self.dimension

        return (x * dimension) + y

    def edge(
        self,
        x: int,
        y: int,
        edges: Optional[List] = None):
        edges = edges if edges else self.edges

        index = self.get_index(x, y)
        return edges[index]

    def set_edge(
        self,
        x: int,
        y: int,
        edge_value: Any,
        edges: Optional[List] = None,
        dimension: Optional[int] = None):
        edges = edges if edges else self.edges

        index = self.get_index(x, y, dimension)
        edges[index] = edge_value
    
    def add(
        self,
        node: Any):
        self.nodes.insert(node)
        
        new_dimension = self.nodes.counter
        new_edges = self.init_edges(new_dimension)

        for x in range(0, new_dimension):
            for y in range(0, new_dimension):
                v = 0 if x == new_dimension-1 or \
                         y == new_dimension-1 \
                        else self.edge(x, y)
                
                self.set_edge(x, y, v, new_edges, new_dimension)

        self.dimension = new_dimension
        self.edges = new_edges
    
    def remove(
        self,
        index: int):
        self.nodes.remove(index)
        new_edges = self.init_edges(self.dimension)

        for x in range(0, self.dimension):
            for y in range(0, self.dimension):
                v = 0 if x == index or y == index \
                        else self.edge(x, y)

                self.set_edge(x, y, v, new_edges)

        self.edges = new_edges

    def get_upstream_index(self, index):
        upstreams = []

        for x in range(0, self.dimension):
            for y in range(0, self.dimension):
                if y == index and self.edge(x, y):
                    upstreams.append(x)
        
        return upstreams

    def get_upstream(self, index):
        upstream_indexes = self.get_upstream_index(index)
        upstreams = []

        for i in upstream_indexes:
            upstreams.append(self.nodes.get(i))
        
        return upstreams

    def get_downstream_index(self, index):
        downstreams = []

        for x in range(0, self.dimension):
            for y in range(0, self.dimension):
                if x == index and self.edge(x, y):
                    downstreams.append(y)
        
        return downstreams
    
    def get_downstream(self, index):
        downstream_indexes = self.get_downstream_index(index)
        downstreams = []

        for i in downstream_indexes:
            downstreams.append(self.nodes.get(i))
        
        return downstreams