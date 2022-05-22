"""Classiq SDK."""

from classiq._internals import logger  # noqa: F401
from classiq._internals.async_utils import (
    enable_jupyter_notebook,
    is_notebook as _is_notebook,
)
from classiq._internals.authentication.authentication import authenticate  # noqa: F401
from classiq._internals.client import configure  # noqa: F401
from classiq._internals.config import Configuration  # noqa: F401
from classiq._version import VERSION as _VERSION
from classiq.analyzer import *  # noqa: F401, F403
from classiq.applications import *  # noqa: F401, F403
from classiq.executor import Executor  # noqa: F401
from classiq.model_designer import *  # noqa: F401, F403
from classiq.quantum_functions import *  # noqa: F401, F403
from classiq.quantum_register import *  # noqa: F401, F403

__version__ = _VERSION


if _is_notebook():
    enable_jupyter_notebook()
