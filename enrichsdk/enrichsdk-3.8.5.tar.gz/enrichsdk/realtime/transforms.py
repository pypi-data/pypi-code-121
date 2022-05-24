"""
Transforms
----------

Modules to transform streaming records

"""
import os
import sys
import json
import logging
from datetime import datetime

logger = logging.getLogger("app")

from .db import RedisBackend

##############################################
# Base classes
##############################################
class TransformBase(object):
    """
    Base for a realtime feature engineering transform
    """

    def __init__(self, *args, **kwargs):
        self.version = "v1.0"
        self.name = self.display = self.__class__.__name__
        self.pipeline = None
        self.args = {}

    def configure(self, pipeline, args):

        self.pipeline = pipeline
        self.logger = pipeline.logger
        self.args = args

        # Override the transform name..
        self.enable = self.args.get("enable", True)
        self.display = self.args.get("display", self.display)
        self.version = self.args.get("version", self.version)

    def initialize(self):
        pass

    def process(self, state):
        pass

    def __str__(self):
        return "{}:{}".format(self.display, self.version)

    def get_pipeline_extra(self):
        if self.pipeline is not None:
            return self.pipeline.get_extra()
        else:
            return {}


##############################################
# DB Access Instances
##############################################
class RedisTransformBase(TransformBase):
    """
    Base class for Redis Read/Write Transforms
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialize(self):
        connparams = self.args.get("connection", {})
        self.backend = RedisBackend(config=connparams)
        self.backend.connect()


class RedisReadTransform(RedisTransformBase):
    """
    Read from Redis
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self, state):

        key = self.args.get("key", None)
        if key is None:
            return state

        streamrow = state.get("streamrow")

        try:
            key = key % streamrow
        except:
            logger.exception("Cant compute the key")
            return state

        name = self.args.get("name", "dbrow")
        dbrow = self.backend.get(key)
        state.put(name, dbrow)

        return state


class RedisWriteTransform(RedisTransformBase):
    """
    Write to Redis
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self, state):

        key = self.args.get("key", None)
        if key is None:
            return state

        streamrow = state.get("streamrow")

        name = self.args.get("name", "dbrow")
        dbrow = state.get(name)

        try:
            key = key % streamrow
        except:
            logger.exception("Cant compute the key from row")
            return state

        try:
            self.backend.post(key, dbrow)
        except:
            logger.exception("Unable to post to backend")
            pass

        return state


##############################################
# Metadata
##############################################
class MetaStartTransform(TransformBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self, state):

        super().process(state)

        streamrow = state.get("streamrow")

        # Insert extra information
        if not "_meta_" in streamrow:
            streamrow["_meta_"] = {}

        streamrow["_meta_"].update({"start_ts": datetime.now().isoformat()})

        state.put("streamrow", streamrow)

        return state


class MetaEndTransform(TransformBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self, state):

        super().process(state)

        streamrow = state.get("streamrow")

        extra = self.get_pipeline_extra()
        extra.update({"end_ts": datetime.now().isoformat()})

        if not "_meta_" in streamrow:
            streamrow["_meta_"] = {}

        streamrow["_meta_"].update(extra)

        return state


class LoggerTransform(TransformBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialize(self):
        name = self.args.get("name", __name__)
        self.logger = logging.getLogger(name)

    def process(self, state):

        super().process(state)

        streamrow = state.get("streamrow")
        dbrow = state.get("dbrow", {})

        # Clean up the record before posting
        streamrow.pop("message", "")
        streamrow["_meta_"].pop("message", "")
        extra = self.args.get("extra", {})
        extra["data"] = {"streamrow": streamrow, "dbrow": dbrow}

        self.logger.debug("Message", extra=extra)

        return state
