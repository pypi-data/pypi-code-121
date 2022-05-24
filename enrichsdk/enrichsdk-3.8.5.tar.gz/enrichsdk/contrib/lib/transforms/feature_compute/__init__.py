import os
import json
import logging
from collections import defaultdict
from datetime import datetime, date, timedelta
from dateutil import parser as dateparser
import pandas as pd

from enrichsdk import Compute, S3Mixin, CheckpointMixin
from enrichsdk.feature_compute import *

logger = logging.getLogger("app")

__all__ = [
    "FeatureComputeBase",
]


class FeatureComputeBase(Compute):
    """
    A built-in transform baseclass to handle standard feature
    computation and reduce the duplication of code.

    This should be used in conjunction with an FeaturesetExtractor & FeatureExtractor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "FeatureComputeBase"
        self._environ = os.environ.copy()

    @classmethod
    def instantiable(cls):
        """
        Return true if class can be instantiated. Override in subclass
        """
        return False

    def get_featureset_extractors(self):
        """
        Get all the *featureset* extractors (not feature extractors)

        Returns:
             list: A list of extractors as a name, extractor combination

        For example::

            return [{
                 "name": "patient",
                 "extractor": <featureset extractor instance>
            }]

        """
        raise Exception("Implement in subclass")

    def store(self, data):
        """
        Store the final result

        Args:
            data (dict): name of featureset -> data associated with it

        """
        raise Exception("Implement in subclass")

    def get_objects(self):
        """
        Get a list of objects (typically names)  to process. Could be dictionaries,
        lists etc. The list is not interpreted by the base class. Could be a list of
        identifier.

        Returns:
           list: A list of objects (could be ids/paths/dicts etc.)

        """
        if "root" not in args:
            raise Exception("Base class implementation required 'root'")

        root = self.args["root"]
        files = os.listdir(root)
        return files

    def read_object(self, obj):
        """
        Read one object returned by get_objects

        Args:
            obj (object): One item in the list of objects

        Returns:
             object: An object like dict or list of dicts

        """

        if "root" not in args:
            raise Exception("Base class implementation required 'root'")

        root = self.args["root"]
        filename = os.path.join(root, obj)
        data = json.load(open(filename))
        return data

    def process(self, state):
        """
        Core loop

        Rough logic::

            get featureset extractors
            get objects
            for each object:
                 for each featureset extractor X
                     process one object with X
                     collect one featureset 'row' for X

            for each featureset extractor X

        """

        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        self.state = state

        # What extractors to run on the data..
        featureset_extractors = self.get_featureset_extractors()
        featureset_extractors = [
            f for f in featureset_extractors if f.get("enable", True)
        ]

        # Go through all the available objects
        objects = self.get_objects()
        logger.debug(f"Received {len(objects)} objects", extra={"transform": self.name})

        # Compute the features..
        final = compute_features(objects, featureset_extractors, self.read_object)

        # Update the frame
        for name, df in final.items():
            if isinstance(df, pd.DataFrame):
                self.update_frame(
                    name + "_features",
                    "Features computed over the available data",
                    df,
                    objects[0],
                )

        # Store the result...
        files = self.store(final)

        registry = self.get_registry()
        dataset = registry.find(list(final.keys()))
        metadata = {
            'files': files
        }
        registry.access(dataset, metadata, 'write')

        logger.debug(
            "Complete execution", extra=self.config.get_extra({"transform": self.name})
        )

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        """
        Check to make sure that the execution completed correctly
        """
        pass
