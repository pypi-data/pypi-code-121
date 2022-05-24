from typing import Any
from typing import Dict
from typing import List

__virtualname__ = "details"


def __virtual__(hub):
    return (
        hasattr(hub, "output"),
        "'rend' needs to be installed in the python environment to use this plugin",
    )


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
    ...


def show(hub, tree: Dict[str, Any]):
    outputter = hub.OPT.rend.output or "nested"
    rendered = hub.output[outputter].display(tree)
    print(rendered)
