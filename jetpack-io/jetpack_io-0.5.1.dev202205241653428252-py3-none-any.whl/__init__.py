from typing import Dict

# __version__ is placeholder
# It gets set in the build/publish process (publish_with_credentials.sh)
__version__ = "0.5.1-dev202205241653428252"

from jetpack.cmd import _root
from jetpack.core._interface import (
    endpoint,
    function,
    jet,
    jetroutine,
    schedule,
    workflow,
)

api_key = ""
"""[Experimental] api_key enables access to a runtime in a jetpack cluster
Any errors with the value will be raised when a jetroutine executes.
"""

__pdoc__: Dict[str, bool] = {}

# Exclude Internal Submodules
_exclude_list = [
    "cmd",
    "config",
    "proto",
    "runtime",
    "util",
]
for key in _exclude_list:
    __pdoc__[key] = False
# Include core Submodule
__pdoc__["core"] = True

__all__ = [
    "function",
    "jet",
    "jetroutine",
    "schedule",
    "workflow",
    "api_key",
    "endpoint",
]


def run() -> None:
    # options can be passed in as env variables with JETPACK prefix
    # e.g. JETPACK_ENTRYPOINT
    _root.cli(auto_envvar_prefix="JETPACK")
