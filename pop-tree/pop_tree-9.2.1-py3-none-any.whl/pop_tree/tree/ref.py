from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


def get(hub, tree, ref: str):
    result = tree
    if ref:
        for key in ref.split("."):
            try:
                result = result[key]
            except KeyError:
                if (
                    "functions" in result
                    and "variables" in result
                    and "attributes" in result
                ):
                    if key in result["functions"]:
                        result = result["functions"][key]
                    elif key in result["variables"]:
                        result = result["variables"][key]
                    elif key in result.get("classes", {}):
                        result = result["classes"][key]
                else:
                    raise

        return {ref: result}
    else:
        return tree


def list_(hub, tree: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return all the references available on the hub by reference first
    """
    ret = {}

    def _get_refs(t: Dict[str, Any]):
        for k, v in t.items():
            if isinstance(v, Dict):
                _get_refs(v)
            elif k == "ref":
                ret[t["ref"]] = t

    _get_refs(tree)

    return ret
