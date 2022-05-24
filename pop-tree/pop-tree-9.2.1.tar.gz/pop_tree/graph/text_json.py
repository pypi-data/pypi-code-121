import json
from typing import Any
from typing import Dict
from typing import List

__virtualname__ = "json"


def _serialize(d: Dict[str, Any]):
    ret = {}
    for k, v in d.items():
        try:
            json.dumps(v)
            ret[k] = v
        except TypeError:
            ret[k] = str(v)
    return ret


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
    return {
        "ref": ref,
        "doc": doc,
        "file": file,
        "attributes": attributes,
        "functions": {k: _serialize(v) for k, v in functions.items()},
        "variables": {k: _serialize(v) for k, v in variables.items()},
        "classes": {k: _serialize(v) for k, v in classes.items()},
    }


def show(hub, tree: Dict[str, Any]):
    serializable_tree = hub.graph.init.recurse(tree)

    print(json.dumps(serializable_tree))
