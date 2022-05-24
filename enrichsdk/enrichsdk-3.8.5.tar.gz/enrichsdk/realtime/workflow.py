"""
Workflow
--------

This module has simple modules for building a realtime transform
pipeline. They are called workflows here to avoid confusion with
'pipeline' used elsewhere.

"""

import traceback
import logging

logger = logging.getLogger("app")

from .transforms import TransformBase


class State(object):
    """
    Internal state objects. Transform classes use this
    state object to store and retrieve state during
    execution.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = {}

    def put(self, name, value):
        self.frames[name] = value

    def get(self, name, default=None):
        return self.frames.get(name, default)

    def dumps(self):
        return str(self.frames.keys())


class WorkflowBase(object):
    """
    Base class to define a workflow. This class registers new
    transforms. Right now it is a simple linear flow. We expect to
    support DAGs in future.

    """

    def __init__(self, *args, **kwargs):
        """ """
        self.config = kwargs.get("config", {})
        self.debug = kwargs.get("debug", False)
        self.transforms = []
        self.logger = logging.getLogger()

    def add(self, specs, **kwargs):

        if not isinstance(specs, list):
            raise Exception("Add expects a list of specifications")

        globalargs = self.config.get("args", {})

        for index, spec in enumerate(specs):

            if issubclass(spec, TransformBase):
                transform = spec
                name = spec.__name__  # class
            elif isinstance(spec, dict):
                if "transform" not in spec:
                    raise Exception(
                        "Spec dictionary should include a 'transform' class"
                    )
                transform = spec["transform"]
                name = spec.get("name", transform.name)
            else:
                raise Exception(f"Unexpected data type {type(spec)}")

            # Instantiate the transform...
            t = transform(**kwargs)

            # Configure it with the new args...
            args = globalargs.get(name, {})
            args["name"] = name
            t.configure(pipeline=self, args=args)

            # Do any other initialization such as connecting to the
            # database..
            t.initialize()

            # Add it and keep it ready for use..
            self.transforms.append(t)

    def process(self, streamrow={}):
        """
        Process one input record obtained from the stream such as
        Kafka.

        """

        state = State()
        state.put("streamrow", streamrow)

        for t in self.transforms:
            try:
                if not t.enable:
                    continue
                t.process(state)
            except:
                logger.exception("Unable to process")
                raise

        return state

    def get_extra(self):
        """
        Generate pipeline metadata
        """
        extra = {}
        if self.debug:
            versions = [str(t) for t in self.transforms]
            extra = {"versions": versions}
        return extra
