import os
import sys
import json
import copy
import re
import traceback
import logging

from ..lib.exceptions import *
from .node import *
from .mixins import *

logger = logging.getLogger("app")

__all__ = [
    "Source",
    "Sink",
    "Compute",
    "Trigger",
    "NotificationIntegration",
    "DatabaseIntegration",
]

##################################################
# Transform objects
##################################################
class Source(Transform):
    """
    This is a special transform that introduces dataframes into the
    state.

    This transform typically extracts information from thirdparty
    tools and services such as APIs, databases.
    """

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.roles_supported = ["Source"]
        self.roles_current = "Source"

    def sample_inputs(self):
        return []

    def is_source(self):
        return True


class Sink(Transform):
    """
    This is a special transform that dumps dataframes that are in the
    state to some thirdparty service such as file system, database,
    cloud storage etc.
    """

    def __init__(self, *args, **kwargs):
        super(Sink, self).__init__(*args, **kwargs)
        self.roles_supported = ["Sink"]
        self.roles_current = "Sink"

    def is_sink(self):
        return True


class Compute(Transform):
    """

    This is a typical transform that wrangles data. It could introduce
    new frames and transform existing frames.

    This will mainly be pandas code but may also be spark/other
    code. The framework itself is agnostic to what the transform
    does.

    """

    def __init__(self, *args, **kwargs):
        super(Compute, self).__init__(*args, **kwargs)
        self.roles_supported = ["Compute"]
        self.roles_current = "Compute"

    def add_marker(self, state, name=None, suffix="Completed"):
        """
        Adds an object to the state to force order. Doesnt
        serve any other purpose

        Parameters
        ----------
        state (obj): State object
        """
        detail = {
            "df": {},
            "transform": self.name,
            "frametype": "dict",
            "params": {},
            "history": [],
        }

        # What should I call the state object?
        if name is None:
            name = self.name
            if suffix is not None:
                name += "_" + suffix

        # Dump it into the shared state
        state.update_frame(name, detail, create=True)


class Trigger(Sink):
    """
    This transform is expected to run after the computation
    is over. This is a particular kind of sync

    .. deprecated:: 2.0

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NotificationIntegration(Integration):
    """
    Search interface dashboard

    .. deprecated:: 2.0

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags.extend(["integration", "notification"])


class DatabaseIntegration(Integration):
    """
    Write to database

    .. deprecated:: 2.0

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags.extend(["integration", "database"])
