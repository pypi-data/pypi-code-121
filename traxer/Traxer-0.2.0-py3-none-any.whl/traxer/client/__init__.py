"""
:mod:`xpipe.client` contains functions and classes needed to interface with the XPipe server API.
It can carry operations like creating/getting an experiment, logging metrics/artefacts/graphs or managing folders. 
"""

from .client import connect
from .experiment import Experiment
from .session import Session

__all__ = ["connect", "Session", "Experiment"]