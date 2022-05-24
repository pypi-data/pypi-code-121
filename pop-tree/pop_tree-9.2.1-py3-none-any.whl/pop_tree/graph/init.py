from typing import Any
from typing import Dict


def __init__(hub):
    hub.graph.GRAPH = None


def is_mod(hub, d: Dict[str, Any]) -> bool:
    """
    Return True if the dictionary looks like the tree's representation of a plugin, else false
    """
    if not all(
        att in d
        for att in (
            "ref",
            "doc",
            "file",
            "attributes",
            "classes",
            "functions",
            "variables",
        )
    ):
        return False
    if not isinstance(d["functions"], dict):
        return False
    if not isinstance(d["variables"], dict):
        return False
    return True


def recurse(hub, d: Dict[str, Any]):
    ret = {}
    for k, v in d.items():
        if isinstance(v, dict):
            if hub.graph.init.is_mod(v):
                ret[k] = getattr(hub.graph, hub.graph.GRAPH).process_mod(**v)
            else:
                ret[k] = hub.graph.init.recurse(v)
        else:
            ret[k] = v
    return ret


def show(hub, tree: Dict[str, Any]):
    getattr(hub.graph, hub.graph.GRAPH).show(tree)
