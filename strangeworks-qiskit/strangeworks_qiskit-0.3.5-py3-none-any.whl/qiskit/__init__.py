"""Strangeworks Qiskit SDK"""

import strangeworks
from .jobs.strangeworksjob import StrangeworksJob
from .provider import StrangeworksProvider, get_backend
import importlib.metadata

__version__ = importlib.metadata.version("strangeworks-qiskit")
