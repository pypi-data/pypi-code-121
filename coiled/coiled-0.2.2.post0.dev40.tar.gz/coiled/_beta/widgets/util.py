from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

import jmespath
from typing_extensions import Literal

from ..states import CombinedProcessStateEnum, get_combined_process_state

try:
    import ipywidgets  # noqa

    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False

try:
    import rich  # noqa

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


SCHEDULER_SEARCH = jmespath.compile("scheduler.instance.instance_type_id")
WORKER_SEARCH = jmespath.compile("workers[*].instance")


def get_worker_statuses(cluster_details) -> Counter[CombinedProcessStateEnum]:
    """Get worker status from a cluster_details response.

    Returns a Counter of the worker statuses listed in `CombinedProcessStateEnum`.
    """
    worker_statuses: Counter[CombinedProcessStateEnum] = Counter(
        get_combined_process_state(worker) for worker in cluster_details["workers"]
    )
    return worker_statuses


def get_instance_types(
    cluster_details: Mapping[str, Any]
) -> tuple[str | None, Counter[str | None]]:
    """Get instance types from a cluster_details response.

    Returns a tuple of schduler_instance_type, Counter(worker_instance_types).
    If the instance type is still not determined, will show "Unknown".
    """
    scheduler_instance_type = SCHEDULER_SEARCH.search(cluster_details) or None
    worker_instance_types = Counter(
        w.get("instance_type_id", None) for w in WORKER_SEARCH.search(cluster_details)
    )
    return scheduler_instance_type, worker_instance_types


def sniff_environment() -> Literal["notebook", "ipython_terminal", "terminal"]:
    """Heuristically determine the execution context.

    This function attempts to determine whether the execution environment is a Jupyter
    Notebook-like context, an IPython REPL context, or the standard Python context.
    The detection is not foolproof and is sensitive to the implementation details of
    the shell.
    """
    try:
        get_ipython  # type: ignore
    except NameError:
        return "terminal"
    ipython = get_ipython()  # type: ignore # noqa: F821
    shell = ipython.__class__.__name__
    if "google.colab" in str(ipython.__class__) or shell == "ZMQInteractiveShell":
        return "notebook"  # Jupyter notebook or qtconsole
    elif shell == "TerminalInteractiveShell":
        return "ipython_terminal"  # Terminal running IPython
    else:
        return "terminal"  # Other type (?)
