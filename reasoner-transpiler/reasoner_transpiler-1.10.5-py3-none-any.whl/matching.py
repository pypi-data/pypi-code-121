"""MATCHing tools."""
from typing import Dict, List

from bmt import Toolkit

from .nesting import Query
from .util import ensure_list, snake_case, space_case, pascal_case

bmt = Toolkit()


def cypher_prop_string(value):
    """Convert property value to cypher string representation."""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return "\"{0}\"".format(
            value.replace("\"", "\\\"")
        )
    if isinstance(value, (float, int)):
        return str(value)
    raise ValueError(f"Unsupported property type: {type(value).__name__}.")


class NodeReference():
    """Node reference object."""

    def __init__(self, node_id, node, **kwargs):
        """Create a node reference.

        All node properties of types [str, bool, float/int] will be enforced
        verbatim EXCEPT for the following reserved properties:
        * categories
        * ids
        * name
        * is_set
        Un-reserved properties with other types will be coerced to str.
        """
        max_connectivity = kwargs.get("max_connectivity", -1)
        self.anonymous = kwargs.get("anonymous", False)

        node = dict(node)  # shallow copy
        self.name = f"`{node_id}`"

        props = {}
        self._filters = []
        self.labels = []

        category = node.pop("categories", None)
        if isinstance(category, list) and len(category) == 1:
            category = category[0]
        if isinstance(category, list):
            self.labels = ['biolink:NamedThing']
            self._filters.append(" OR ".join([
                "{1} in labels({0})".format(
                    self.name,
                    cypher_prop_string(ci)
                )
                for ci in category
            ]))
        elif category is not None:
            # coerce to a string
            self.labels = [str(category)]

        curie = node.pop("ids", None)
        if isinstance(curie, list) and len(curie) == 1:
            curie = curie[0]
        if isinstance(curie, list):
            self._filters.append("{0}.id in [{1}]".format(
                self.name,
                ", ".join([
                    cypher_prop_string(ci)
                    for ci in curie
                ])
            ))
        elif curie is not None:
            # coerce to a string
            props["id"] = str(curie)

        if max_connectivity > -1:
            self._filters.append("size( ({0})-[]-() ) < {1} + 1".format(
                self.name,
                max_connectivity,
            ))

        props.update(
            (key, value)
            for key, value in node.items()
            if key not in ("name", "is_set", "constraints")
        )

        self.prop_string = "{" + ", ".join([
            f"`{key}`: {cypher_prop_string(value)}"
            for key, value in props.items()
            if value is not None and not key.startswith("_")
        ]) + "}" if props else ""
        self._hints = []
        if curie and self.labels:
            self._hints.append(f"USING INDEX {self.name}:`{self.labels[0]}`(id)")
        self._num = 0

    def __str__(self):
        """Return the cypher node reference."""
        self._num += 1
        if self._num > 1:
            return f"({self.name})"
        ref = "("
        elements = []
        if not self.anonymous:
            elements.append(self.name)
        if self.labels:
            elements.append("".join(f":`{label}`" for label in self.labels))
        elements = ["".join(elements)]
        if self.prop_string:
            elements.append(self.prop_string)
        ref = "({})".format(" ".join(elements))
        return ref

    @property
    def filters(self):
        """Return filters for the cypher node reference.

        To be used in a WHERE clause following the MATCH clause.
        """
        if self._num > 1:
            return []
        return self._filters

    @property
    def hints(self):
        """Return hints for the cypher node reference.

        To be appended to the MATCH clause.
        """
        if self._num > 1:
            return []
        return self._hints


class MissingReference(NodeReference):
    """Missing node reference object."""

    def __init__(self, name):  # pylint: disable=super-init-not-called
        """Initialize."""
        self.name = f"`{name}`"
        self._num = 2


class EdgeReference():
    """Edge reference object."""

    def __init__(
        self,
        edge_id,
        edge,
        anonymous=False,
        invert=True,
    ):
        """Create an edge reference."""
        edge = dict(edge)  # make shallow copy
        _subject = edge.pop("subject")
        _object = edge.pop("object")
        self.name = edge_id if not anonymous else ""
        self.predicates: List[str] = ensure_list(
            edge.pop("predicates", []) or []
        )
        self.filters = []
        self.label = None
        self.length = edge.pop("_length", (1, 1))
        invert = invert and edge.pop("_invert", True)

        self.inverse_predicates = []
        self.directed = False
        for predicate in self.predicates:
            el = bmt.get_element(space_case(predicate[8:]))
            if el is None:
                symmetric = False
                inverse = None
            else:
                inverse = el.inverse
                symmetric = el.symmetric
            # relationship is directed if any provided predicate is asymmetrical
            if not symmetric:
                self.directed = True
            if inverse is not None:
                self.inverse_predicates.append(f"biolink:{snake_case(inverse)}")
            elif symmetric:
                self.inverse_predicates.append(predicate)

        # get all descendant predicates
        self.predicates = [
            f"biolink:{snake_case(p)}"
            for predicate in self.predicates
            for p in bmt.get_descendants(space_case(predicate[8:]))
        ]
        if not invert:
            self.inverse_predicates = []
        self.inverse_predicates = [
            f"biolink:{snake_case(p)}"
            for predicate in self.inverse_predicates
            for p in bmt.get_descendants(space_case(predicate[8:]))
        ]

        self.label = "|".join(
            f"`{predicate}`"
            for predicate in self.predicates + self.inverse_predicates
        )

        if self.inverse_predicates:
            self.directed = False
            self.filters.append(" OR ".join([
                "(type(`{0}`) in [{1}] AND startNode(`{0}`) = `{2}`)".format(
                    self.name,
                    ", ".join([
                        f"\"{predicate}\""
                        for predicate in self.predicates
                    ]),
                    _subject,
                ),
                "(type(`{0}`) in [{1}] AND startNode(`{0}`) = `{2}`)".format(
                    self.name,
                    ", ".join([
                        f"\"{predicate}\""
                        for predicate in self.inverse_predicates
                    ]),
                    _object,
                ),
            ]))

        props = {}
        props.update(
            (key, value)
            for key, value in edge.items()
            if key not in ("name", "constraints") and not key.startswith("_")
        )

        self.prop_string = " {" + ", ".join([
            f"`{key}`: {cypher_prop_string(value)}"
            for key, value in props.items()
            if value is not None
        ]) + "}" if props else ""

    def __str__(self):
        """Return the cypher edge reference."""
        elements = [
            f":{self.label}" if self.label else "",
        ]
        if not self.length == (1, 1):
            elements.append("*{}..{}".format(
                self.length[0] if self.length[0] is not None else "",
                self.length[1] if self.length[1] is not None else "",
            ))
        elements.append(f"{self.prop_string}")
        return "-[`{0}`{1}]-".format(
            self.name,
            "".join(elements),
        ) + (">" if self.directed else "")


def build_match_clause(
        *patterns,
        filters=None,
        hints=None,
        **kwargs,
):
    """Build MATCH clause (and subclauses) from components."""
    query = ""
    query += "MATCH " + ", ".join(patterns)
    if kwargs.get("use_hints", False) and hints:
        query += " " + " ".join(hints)
    if filters:
        if len(filters) > 1:
            filters = [f"({f})" for f in filters]
        query += " WHERE " + " AND ".join(filters)

    return query


def match_edge(
    qedge_id,
    qedge,
    node_references: Dict[str, NodeReference],
    invert=True,
    **kwargs,
):
    """Get MATCH clause for edge."""
    eref = EdgeReference(qedge_id, qedge, invert=invert)
    source_node = node_references[qedge["subject"]]
    target_node = node_references[qedge["object"]]
    pattern = f"{source_node}{eref}{target_node}"
    edge_filters = [
        f"({c})"
        for c in source_node.filters + target_node.filters + eref.filters
    ]
    return build_match_clause(
        pattern,
        hints=source_node.hints + target_node.hints,
        filters=edge_filters,
        **kwargs,
    )


def match_query(qgraph, subclass=True, **kwargs):
    """Generate a Cypher MATCH clause.

    Returns the query fragment as a string.
    """
    if subclass:
        superclasses = {
            qnode_id + "_superclass": {
                "ids": qnode.pop("ids"),
                "categories": qnode.pop("categories", None),
                "_return": False,
            }
            for qnode_id, qnode in qgraph["nodes"].items()
            if qnode.get("ids", None) is not None
        }
        subclass_edges = {
            qnode_id[:-11] + "_subclass_edge": {
                "subject": qnode_id[:-11],
                "object": qnode_id,
                "predicates": ["biolink:subclass_of"],
                "_length": (0, 1),
                "_invert": False,
                "_return": False,
            }
            for qnode_id in superclasses
        }
        qgraph["nodes"].update(superclasses)
        qgraph["edges"].update(subclass_edges)

    # sets of ids
    defined_nodes = set(qgraph["nodes"])
    defined_edges = set(qgraph["edges"])
    referenced_nodes = set(
        [e["subject"] for e in qgraph["edges"].values()]
        + [e["object"] for e in qgraph["edges"].values()]
    )

    # generate internal node and edge variable names
    node_references = {
        qnode_id: NodeReference(qnode_id, qnode, **kwargs)
        for qnode_id, qnode in qgraph["nodes"].items()
    }
    for node_id in referenced_nodes - defined_nodes:  # reference-only nodes
        node_references[node_id] = MissingReference(node_id)

    clauses = []

    # match orphaned nodes
    for node_id in defined_nodes - referenced_nodes:
        clauses.append(build_match_clause(
            str(node_references[node_id]),
            hints=node_references[node_id].hints,
            filters=node_references[node_id].filters,
            **kwargs,
        ))

    # match edges
    for qedge_id, qedge in qgraph["edges"].items():
        clauses.append(match_edge(
            qedge_id,
            qedge,
            node_references,
            **kwargs,
        ))

    return Query(
        " ".join(clauses),
        qids=defined_nodes | defined_edges,
        references=defined_nodes | referenced_nodes | defined_edges,
        qgraph=qgraph,
    )
