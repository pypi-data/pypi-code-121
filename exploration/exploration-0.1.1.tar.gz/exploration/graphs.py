"""
- Authors: Peter Mawhorter
- Consulted:
- Date: 2022-3-5
- Purpose: Low-level graph helpers & types.

This file defines tools on top of the `networkx` package which are
lower-level than the key types used for most tasks (see `core.py` for
those).
"""

from typing import (
    Optional, Hashable, Dict, Union, Iterable, Tuple, Any, NoReturn,
    Set, Sequence, cast, List
)

import networkx as nx # type: ignore[import]


Node = Hashable
"Type alias for graph nodes."


Edge = Hashable
"Type alias for graph edges."


class UniqueExitsGraph(nx.MultiDiGraph):
    """
    A `networkx.MultiDiGraph` which has unique-per-source-node names for
    each edge. On top of base functionality, this uses some extra memory
    to store per-edge outgoing (but not incoming) by-edge dictionaries,
    so that you can iterate over edges by their names rather than
    iterating over neighbor nodes. This helps in some circumstances where
    you know the edge name but not the name of the room it connects to.

    This does NOT change the meaning of any of the built-in
    `networkx.MultiDiGraph` methods, but instead adds new methods for
    access to nodes or attributes by node -> edge name.
    """
    def __init__(self) -> None:
        super().__init__()
        # A dictionary that maps nodes to edge names, storing neighbor
        # nodes for each edge. Those neighbor nodes can be used to look
        # up edge attributes using the normal MultiDiGraph machinery.
        self._byEdge: Dict[Node, Dict[Edge, Node]] = {}

    def new_edge_key(self, u: Node, v: Node) -> NoReturn:
        """
        This method would normally be used to generate new edge keys. We
        disable it, because we want to ensure that all edges are properly
        labeled.
        """
        raise NotImplementedError(
            "Attempted to add an edge without specifying a key!"
        )

    def add_node(self, node: Node, **attr: Any):
        """
        See `networkx.MultiDiGraph.add_node`.
        """
        super().add_node(node, **attr)
        self._byEdge[node] = {} # type Dict[Edge, Node]

    def add_nodes_from(
        self,
        nodes: Union[
            Iterable[Node],
            Iterable[Tuple[Node, Dict[Any, Any]]]
        ],
        **attr: Any
    ):
        """
        See `networkx.MultiDiGraph.add_nodes_from`.
        """
        super().add_nodes_from(nodes, **attr)
        # Reassignment during tuple unpacking is not checkable...
        n: Any
        for n in nodes:
            # Test for hashability & unpack tuple if not
            try:
                self._byEdge.get(n)
            except TypeError:
                n, _ = n # mypy can't handle this properly
            self._byEdge[n] = {}

    def remove_node(self, node: Node):
        """
        See `networkx.MultiDiGraph.remove_node`.
        """
        # Handle deletion from inherited structures
        super().remove_node(node)

        # Ignore if not present
        if node not in self._byEdge:
            return

        # Remove record of outgoing edges
        del self._byEdge[node]

        # Remove incoming edge records
        for source, edgeMap in self._byEdge.items():
            delete = []
            # Find all edges which go to the deleted node
            # (this is not terribly efficient)
            for edgeName, dest in edgeMap.items():
                if dest == node:
                    delete.append(edgeName)
            # Delete them in a separate loop, so that we don't
            # modify-while-iterating (not efficient and maybe
            # unnecessary?)
            for d in delete:
                del edgeMap[d]

    def remove_nodes_from(self, nodes: Iterable[Node]):
        """
        See `networkx.MultiDiGraph.remove_nodes_from`.
        """
        # First use inherited method to remove from inherited structures
        super().remove_nodes_from(nodes)
        # remove our custom info
        for n in nodes:
            if n in self._byEdge:
                del self._byEdge[n]

            for source, edgeMap in self._byEdge.items():
                delete = []
                # Find all edges that go to any deleted node
                for edgeName, dest in edgeMap.items():
                    if dest in nodes:
                        delete.append(edgeName)

                # Remove edges in separate loop to avoid
                # modifying-while-iterating (not efficient and maybe
                # unnecessary?)
                for d in delete:
                    del edgeMap[d]

    def add_edge(
        self,
        u_of_edge: Node,
        v_of_edge: Node,
        key: Edge,
        **attr: Any
    ) -> Edge:
        """
        See `networkx.MultiDiGraph.add_edge`.

        For a `UniqueExitsGraph`, an edge key must be supplied
        explicitly. A `KeyError` will be raised if an edge using the
        given key (i.e., name) already exists starting at the source node
        (regardless of its destination!).

        Returns the key it was given, to match the base `add_edge` API.
        """
        if u_of_edge in self._byEdge and key in self._byEdge[u_of_edge]:
            raise KeyError(
                f"Cannot add a second edge '{key}' starting at node"
                f" '{u_of_edge}'."
            )
        super().add_edge(u_of_edge, v_of_edge, key, **attr)
        # Note: the base add_edge function does NOT call our add_node
        # function :(
        if u_of_edge not in self._byEdge:
            self._byEdge[u_of_edge] = {}
        if v_of_edge not in self._byEdge:
            self._byEdge[v_of_edge] = {}
        # Add the edge to our by-edge-name structure
        self._byEdge[u_of_edge][key] = v_of_edge

        return key

    def add_edges_from(
        self,
        ebunch_to_add: Any,
        # Type should be this, but checker won't pass it:
        #Union[
        #    Iterable[Tuple[Node, Node, Edge]],
        #    Iterable[Tuple[Node, Node, Edge, Dict[Any, Any]]]
        #],
        **attr: Any
    ):
        """
        See `networkx.MultiDiGraph.add_edges_from`. Tuples in the ebunch
        must be 3- or 4-tuples that include a specific key (not just
        data). Nodes will be created as necessary.

        Raises a `KeyError` if adding an edge is impossible because it
        re-uses the same edge name at a particular source node, but if an
        attempt is made to add an existing edge with the same
        destination, this will just update the relevant edge attributes.

        Raises a `KeyError` instead of silently updating edge properties
        if the existing edge was also added by an earlier entry in the
        `ebunch_to_add` (i.e., if you are trying to add two edges at
        once that go between the same pair of nodes and use the same
        edge key).

        >>> from exploration import graphs as eg
        >>> g = eg.UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.nodes
        NodeView(('A', 'B', 'C'))
        >>> for edge in g.edges:
        ...    print(edge)
        ('A', 'B', 'up')
        ('A', 'B', 'up2')
        ('B', 'A', 'down')
        ('B', 'B', 'self')
        ('B', 'C', 'next')
        ('C', 'B', 'prev')
        """
        etuple: Any
        for i, etuple in enumerate(ebunch_to_add):
            if len(etuple) < 3:
                raise ValueError(
                    f"Edges to add must contain explicit keys for a"
                    f" UniqueExitsGraph (edge #{i} had only 2 parts)."
                )
            try:
                hash(etuple[2])
            except TypeError:
                raise ValueError(
                    f"Edges to add must contain explicit keys for a"
                    f" UniqueExitsGraph (edge #{i} had an unhashable 3rd"
                    f" component)."
                )

            # Check edge name uniqueness
            u, v, k = etuple[:3]
            if u in self._byEdge and self._byEdge[u].get(k) != v:
                raise KeyError(
                    f"Cannot add or update an edge named '{k}' from node"
                    f" '{u}' to node '{v}' because an edge by that name"
                    f" already exists and goes to a different"
                    f" destination."
                )

        # Add edges to inherited structures
        super().add_edges_from(ebunch_to_add, **attr)

        # Note base implementation calls add_edge, so we don't need to
        # add edges to our extra structure

    def remove_edge(self, u_of_edge: Node, v_of_edge: Node, key: Edge):
        """
        See `networkx.MultiDiGraph.remove_edge`. A key is required in
        this version to specify which edge we're removing.

        Raises a NetworkXError if the target edge does not exist.
        """
        super().remove_edge(u_of_edge, v_of_edge, key)
        del self._byEdge[u_of_edge][key]

    def remove_edges_from(
        self,
        ebunch: Union[
            Iterable[Tuple[Node, Node, Edge]],
            Iterable[Tuple[Node, Node, Edge, Dict[Any, Any]]]
        ]
    ):
        """
        See `networkx.MultiDiGraph.remove_edges_from`. Edge tuples in
        the ebunch must be 3- or 4-tuples that include a key.

        If an edge being removed is not present, it will be ignored.
        """
        if any(len(etuple) not in (3, 4) for etuple in ebunch):
            raise ValueError(
                "Edges to remove must be u, v, k 3-tuples or u, v, k, d"
                " 4-tuples."
            )
        super().remove_edges_from(ebunch)
        # This calls self.remove_edge under the hood so we don't need
        # extra cleanup steps for _byEdge.

    def clear(self) -> None:
        """
        See `networkx.MultiDiGraph.clear`.
        """
        super().clear()
        self._byEdge.clear()

    def clear_edges(self) -> None:
        """
        See `networkx.MultiDiGraph.clear_edges`.
        """
        super().clear_edges()
        for _, edgeMap in self._byEdge.items():
            edgeMap.clear()

    def reverse(self) -> NoReturn:
        """
        See `networkx.MultiDiGraph.reverse`.
        """
        raise NotImplementedError(
            "Reversing a UniqueExitsGraph is not supported because"
            " reversed edge names might not be unique."
        )

    def removeEdgeByKey(self, uOfEdge: Node, key: Edge):
        """
        Removes an edge sourced at a particular node that has a
        particular key, without knowing what the destination is.

        Raises a `KeyError` if the named edge does not exist.

        ## Example

        >>> g = UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.getDestination('A', 'up')
        'B'
        >>> g.getDestination('A', 'up2')
        'B'
        >>> g.getDestination('B', 'self')
        'B'
        >>> g.removeEdgeByKey('A', 'up2')
        >>> g.removeEdgeByKey('B', 'self')
        >>> g.getDestination('A', 'up2') is None
        True
        >>> g.getDestination('B', 'self') is None
        True
        """
        vOfEdge = self._byEdge[uOfEdge][key]
        super().remove_edge(uOfEdge, vOfEdge, key)
        del self._byEdge[uOfEdge][key]

    def removeEdgesByKey(self, edgeIds: Iterable[Tuple[Node, Edge]]):
        """
        Removes multiple edges by source node and key, without needing
        to know destination nodes. The `edgeIds` argument must be a list
        of tuples containing source node, edge key pairs.

        Silently ignores already-nonexistent edges.

        ## Example

        >>> g = UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.getDestination('A', 'up')
        'B'
        >>> g.getDestination('A', 'up2')
        'B'
        >>> g.getDestination('B', 'self')
        'B'
        >>> g.removeEdgesByKey([('A', 'up2'), ('B', 'self')])
        >>> g.getDestination('A', 'up2') is None
        True
        >>> g.getDestination('B', 'self') is None
        True
        """
        for source, key in edgeIds:
            if key in self._byEdge.get(source, {}):
                self.removeEdgeByKey(source, key)
            # Otherwise ignore this edge...

    def destinationsFrom(self, source: Node) -> Dict[Edge, Node]:
        """
        Given a source node, returns a dictionary mapping the keys of all
        outgoing edges from that node to their destination nodes. Raises
        a `KeyError` if the node is not present in the graph.

        Editing the dictionary returned could cause serious problems, so
        please don't.

        ## Example

        >>> g = UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.destinationsFrom('A')
        {'up': 'B', 'up2': 'B'}
        >>> g.destinationsFrom('B')
        {'down': 'A', 'self': 'B', 'next': 'C'}
        >>> g.destinationsFrom('C')
        {'prev': 'B'}
        >>> g.destinationsFrom('D')
        Traceback (most recent call last):
        ...
        KeyError...
        """
        return self._byEdge[source]

    def destination(self, source: Node, edge: Edge) -> Node:
        """
        Given a source node and an edge key, looks up and returns the
        destination node for that edge. Raises a `KeyError` if there is no
        edge from the specified node with the specified name.

        ## Example

        >>> g = UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.destination('A', 'up')
        'B'
        >>> g.destination('A', 'up2')
        'B'
        >>> g.destination('B', 'down')
        'A'
        >>> g.destination('A', 'nonexistent')
        Traceback (most recent call last):
        ...
        KeyError...
        >>> g.destination('D', 'any')
        Traceback (most recent call last):
        ...
        KeyError...
        """
        return self._byEdge[source][edge]

    def getDestination(
        self,
        source: Node,
        edge: Edge,
        default: Any = None
    ) -> Optional[Node]:
        """
        Works like `destination`, but instead of raising a `KeyError` if
        the node or edge is missing, it returns a default value (with a
        default default of `None`).

        ## Example

        >>> g = UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.getDestination('A', 'up')
        'B'
        >>> g.getDestination('A', 'up2')
        'B'
        >>> g.getDestination('B', 'down')
        'A'
        >>> g.getDestination('A', 'nonexistent') is None
        True
        >>> g.getDestination('A', 'nonexistent', 'default')
        'default'
        >>> g.destination('D', 'any') is None
        True
        """
        return self._byEdge.get(source, {}).get(edge, default)

    def allEdgesTo(
        self,
        destination: Node
    ) -> List[Tuple[Node, Edge]]:
        """
        Searches the entire graph for edges whose destinations are the
        specified destination, and returns a list of (node, edge) pairs
        indicating the source node and edge name for each of those edges.

        ## Example

        >>> g = UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> g.allEdgesTo('A')
        [('B', 'down')]
        >>> g.allEdgesTo('B')
        [('A', 'up'), ('A', 'up2'), ('C', 'prev')]
        >>> g.allEdgesTo('C')
        [('B', 'next')]
        >>> g.allEdgesTo('D')
        []
        """
        results = []
        for node in self:
            fromThere = self.edges[node]
            for dest in fromThere:
                if dest == destination:
                    for edge in fromThere:
                        results.append((node, edge))

        return results

    def textMapObj(
        self,
        edgeSep: str = '::',
        external: Optional[Set[Node]] = None,
        explorationOrder: Tuple[Node, Sequence[Edge]] = None,
        edgeOrders: Union[
            Dict[Node, Sequence[Edge]],
            Dict[Node, Dict[Edge, Any]]
        ] = None
    ):
        """
        Returns a special object which is JSON-serializable and which
        when serialized creates a semi-human-usable text-format map of
        the graph.

        The object consists of nested dictionaries, one per node, where
        keys are node name + edge name strings (combined using the
        `edgeSep` argument, default is '::'). The value for each key is
        one of:

        1. Another dictionary representing the node that edge leads
            to, which can in turn have dictionary values...
        2. A string naming a destination node that's already represented
            elsewhere (or naming the current node for self-edges).

        Any node present in the specified `external` set will be linked
        to instead of listed out, even if it exists in the graph. The
        `external` set **will be modified** by this function to include
        all visited nodes in the graph.

        If an `explorationOrder` is provided, it must be a tuple
        specifying a start node followed by a sequence of edges that
        indicates the path taken, and the edges will be visited
        according to that order (this only matters in Python 3.7+ where
        dictionaries have consistent order). A `ValueError` will be
        raised if an invalid exploration order is provided. The path
        list will be ignored if `edgeOrders` is provided explicitly.

        TODO: What about unexplorable graphs (allow node names in place
        of edge names in exploration order?)?!?

        If `edgeOrders` is provided directly, it will override the
        path part of the `explorationOrder` to determine the ordering of
        edges at each node. If not and `explorationOrder` is provided, it
        will be deduced from the `explorationOrder`. If neither is
        present, ordering will follow whatever natural order is in the
        graph, which in most cases should be order-of-creation.

        Notes:
        - For the format to avoid ambiguity, the `edgeSep` value must be
            a string which does not appear in any node or edge names.
        - Nodes and edge values will be converted to strings to build the
            map.
        - Node and edge properties are not represented in the resulting
            object.
        - For a variety of reasons, the result cannot be converted back
            to a graph object. This is not intended for use as a JSON
            serialization route (see the `networkx.readwrite.json_graph`
            module for some built-in options).
        - To get a string representation, one could do:
            `json.dumps(graph.textMapObj())`

        ## Examples

        >>> from exploration import graphs as eg
        >>> import json
        >>> g = eg.UniqueExitsGraph()
        >>> g.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> print(json.dumps(g.textMapObj(), indent=2))
        {
          "A::up": {
            "B::down": "A",
            "B::self": "B",
            "B::next": {
              "C::prev": "B"
            }
          },
          "A::up2": "B"
        }
        """
        # We use `external` as our visited set
        if external is None:
            external = set()

        if explorationOrder is not None:
            here, path = explorationOrder
        else:
            # Find first non-external node as our starting node
            for here in self.nodes:
                if here not in external:
                    break

            # Path is empty
            path = []

        # Determine edge ordering for each node from exploration order
        # or by natural ordering if no explorationOrder is available
        if edgeOrders is None:
            edgeOrders = cast(
                Dict[Node, Dict[Edge, Any]],
                {}
            )
            current = here
            for i in range(len(path)):
                edge = path[i]
                # Add this edge next in the ordering for this node
                orderHere = cast(
                    Dict[Edge, Any],
                    edgeOrders.setdefault(current, {})
                )
                # Note: we use a dictionary here because dictionaries do
                # preserve insertion ordering (3.7+) and we need to both
                # keep things in order AND do a bunch of lookups to
                # avoid duplicates.
                if edge not in orderHere:
                    orderHere[edge] = True

                # Move to next node
                if edge not in self._byEdge[current]:
                    raise ValueError(
                        f"Invalid edge in exploration order path: at"
                        f" step {i} we reached node {current} and were"
                        f" supposed to take edge {edge} but that edge"
                        f" does not exist."
                    )
                current = self._byEdge[current][edge]

            # Add any unexplored nodes and/or edges in natural order
            for node in self.nodes:
                orderHere = edgeOrders.setdefault(node, {})
                for edge in self._byEdge[node]:
                    if edge not in orderHere:
                        orderHere[edge] = True

        result = {}
        external.add(here)
        # Now loop through keys of this node
        for key in edgeOrders[here]:
            combined = str(here) + edgeSep + str(key)
            dest = self._byEdge[here][key]
            if dest in external:
                # links, including self-links
                result[combined] = str(dest)
            else:
                # Recurse
                result[combined] = self.textMapObj(
                    edgeSep,
                    external,
                    (dest, []), # empty path since we have edgeOrders
                    edgeOrders
                )

        return result
