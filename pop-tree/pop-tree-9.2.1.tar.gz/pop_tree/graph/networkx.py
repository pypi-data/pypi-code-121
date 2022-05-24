from enum import IntEnum
from typing import Any
from typing import Dict
from typing import List

try:
    import networkx as nx
    import matplotlib.cm as cmx
    import matplotlib.colors as colors
    import matplotlib.pyplot as plt

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def __init__(hub):
    # A collection of nodes (vertices) along with identified pairs of nodes (called edges, links, etc).
    hub.graph.networkx.GRAPH = nx.Graph(name="hub")


class NodeType(IntEnum):
    hub = 0
    sub = 1
    plugin = 2
    function = 3
    contract = 6
    variable = 4
    class_ = 5
    unknown = 7


def add_node(hub, ref: str, node_type: NodeType = NodeType.unknown, **attrs):
    builder = []
    for name in ref.split("."):
        parent = ".".join(builder)
        cur_ref = ".".join(builder + [name])
        if cur_ref not in hub.graph.networkx.GRAPH.nodes:
            hub.graph.networkx.GRAPH.add_node(
                cur_ref, name=name, node_type=NodeType.sub
            )
        hub.graph.networkx.GRAPH.add_edge(parent, cur_ref)
        builder.append(name)

    # The last thing in the list gets all the attrs
    if attrs:
        hub.graph.networkx.GRAPH.add_node(
            cur_ref, name=name, node_type=node_type, **attrs
        )


def add_edge(
    hub, ref1: str, ref2: str, node_type: NodeType = NodeType.unknown, **ref2_attrs
):
    hub.graph.networkx.add_node(ref2, node_type=node_type, **ref2_attrs)
    hub.graph.networkx.GRAPH.add_edge(ref1, ref2)


def process_mod(
    hub,
    ref: str,
    doc: str,
    file: str,
    attributes: List[str],
    functions: Dict[str, Dict[str, Any]],
    variables: Dict[str, Dict[str, Any]],
    classes: Dict[str, Dict[str, Any]],
):
    hub.graph.networkx.add_node(
        ref, doc=doc, file=file, attributes=attributes, node_type=NodeType.plugin
    )

    for name, function in functions.items():
        if "functions" in hub.OPT.pop_tree.hide:
            continue
        if (
            any(function["contracts"].get(c) for c in ("pre", "call", "post"))
            and "contracts" not in hub.OPT.pop_tree.hide
        ):
            previous = None
            for c in (
                function["contracts"]["pre"]
                + function["contracts"]["call"]
                + [function["ref"]]
                + function["contracts"]["post"]
            ):
                if c == function["ref"]:
                    node_type = NodeType.function
                else:
                    node_type = NodeType.contract
                hub.graph.networkx.GRAPH.add_node(
                    c, name=c.split(".")[-1], node_type=node_type
                )
                if previous is None:
                    hub.graph.networkx.GRAPH.add_edge(ref, c, doc=doc)
                else:
                    hub.graph.networkx.GRAPH.add_edge(previous, c)
                previous = c
        else:
            hub.graph.networkx.add_edge(
                ref, function["ref"], doc=doc, node_type=NodeType.function
            )

    for name, variable in variables.items():
        if "variables" in hub.OPT.pop_tree.hide:
            continue
        hub.graph.networkx.add_edge(
            ref,
            variable["ref"],
            type=variable["type"],
            value=variable["value"],
            node_type=NodeType.variable,
        )

    for name, cls in classes.items():
        if "classes" in hub.OPT.pop_tree.hide:
            continue
        hub.graph.networkx.add_edge(ref, cls["ref"], node_type=NodeType.class_)


def show(hub, tree: Dict[str, Any]):
    hub.graph.init.recurse(tree)
    hub.graph.networkx.GRAPH.add_node("", name="hub", node_type=NodeType.hub)

    # All nodes should point to themselves down the line
    graph: nx.GRAPH = hub.graph.networkx.GRAPH
    # from pprint import pprint
    # print(dict(graph.adjacency()))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    layout = hub.OPT.pop_tree.graph_layout or "kamada_kawai"
    pos_nodes = getattr(nx, f"{layout}_layout")(graph)
    cmap = plt.cm.get_cmap("Set2")
    color_norm = colors.Normalize(vmin=min(NodeType), vmax=max(NodeType))
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap=cmap)
    for item in NodeType:
        ax.plot(
            [0], [0], color=scalar_map.to_rgba(item.value), label=item.name.strip("_")
        )
    nx.draw(
        graph,
        pos_nodes,
        vmin=min(NodeType),
        vmax=max(NodeType),
        node_color=[
            v.value for v in nx.get_node_attributes(graph, "node_type").values()
        ],
        cmap=cmap,
    )
    plt.legend()
    names = nx.get_node_attributes(graph, "name")
    nx.draw_networkx_labels(graph, pos_nodes, labels=names)
    plt.legend()
    fig.tight_layout()
    plt.show()
