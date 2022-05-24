from collections import namedtuple
from typing import Any
from typing import Dict
from typing import List

__virtualname__ = "simple"

Plugin = namedtuple("Plugin", ("functions", "variables"))


def __virtual__(hub):
    return (
        hasattr(hub, "output"),
        "'rend' needs to be installed in the python environment to use this plugin",
    )


def _keys(d: Dict[str, Any]) -> List[str]:
    return [k for k in d.keys()]


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
    return Plugin(functions=_keys(functions), variables=_keys(variables))


def show(hub, tree: Dict[str, Any]):
    simple_tree = hub.graph.init.recurse(tree)

    outputter = hub.OPT.rend.output or "nested"
    rendered = hub.output[outputter].display(simple_tree)
    print(rendered)
