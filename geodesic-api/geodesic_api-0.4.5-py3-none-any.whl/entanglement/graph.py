try:
    from networkx import DiGraph
    networkx_available = True
except ImportError:
    networkx_available = False

    class DiGraph:
        pass


class Graph(DiGraph):
    def __init__(self, data=None, nodes=None, edges=None, project=None) -> None:
        super().__init__()
        if not networkx_available:
            raise ImportError("networkx not available. Must be installed to use Graph")

        if nodes is not None:
            self.add_nodes_from(nodes)

            for node in nodes:
                node.graph = self

        if edges is not None:
            for connection in edges:
                p = connection.predicate
                self.add_edge(
                    connection.subject,
                    connection.object,
                    connection=connection,
                    name=p.name,
                    **connection.predicate.edge_attributes
                )
