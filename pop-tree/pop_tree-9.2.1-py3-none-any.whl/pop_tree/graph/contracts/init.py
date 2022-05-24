from typing import Any
from typing import Dict
from typing import List


def sig_show(hub, tree: Dict[str, Any]):
    ...


def sig_process_mod(
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
