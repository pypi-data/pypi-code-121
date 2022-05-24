"""
Transforms
^^^^^^^^^^

This class bridges expectations library and the Enrich pipelines. 
"""

import os
import sys
import imp
import json
import logging
import pickle
import traceback

from .exceptions import *
from .expectations import *

logger = logging.getLogger("app")


class TransformExpectation(object):
    """
    Class to provide a bridging interface between light weight
    expectations implemented here and the pipeline
    """

    def __init__(self, transform, mode=None, filename=None, expectations=None):
        """
        Initialize the class

        Args:
           transform: Transform using this expectation
           mode: Mode of operation (validation|generation)
           filename: Path to expectations file
           expectations: Explicitly provide expectations

        Returns:
           Instantiated class

        """
        self.transform = transform
        assert mode in ["validation", "generation", None]

        if (filename is None) and (expectations is None):
            raise InvalidExpectation("Missing expectations and filename")
        elif (filename is not None) and (expectations is not None):
            raise InvalidExpectation("Cant specify both expectations and filename")

        if filename is not None:
            filename = transform.config.get_file(filename)

        self.mode = mode
        if self.mode == "validation":
            if filename is not None:
                if not os.path.exists(filename):
                    raise InvalidExpectation("Missing expectations file")
            elif expectations is not None:
                if not isinstance(expectations, list):
                    raise InvalidExpectation("Expectations should be a list")

        if expectations is not None:
            self.expectations = expectations
        else:
            self.expectations = []

        try:
            if (mode == "validation") and (filename is not None):
                self.expectations = self.load_expectations_file(filename)
        except:
            raise InvalidExpectation("Invalid expectation file")

    def load_expectations_file(self, filename):
        """Load expectations whether specified as json, pickle, or py
        file into a instance variable.

        Args:
            filename: Name of the expectations file

        Returns:
            None:

        """
        self.filename = filename
        if filename.endswith(".json"):
            return json.load(open(filename))

        if filename.endswith(".pkl"):
            return pickle.load(open(filename, "rb"))

        if filename.endswith(".py"):
            try:

                modname = os.path.basename(filename)
                dirname = os.path.dirname(filename)

                if modname.endswith(".py"):
                    modname = modname.replace(".py", "")

                file_, path_, desc_ = imp.find_module(modname, [dirname])
                package = imp.load_module(modname, file_, path_, desc_)
                return package.expectations
            except:
                logger.exception(
                    "Skipping. Expectations file could not be read",
                    extra=self.get_extra(
                        {
                            "transform": self.transform,
                            "data": "Filename: {}".format(filename),
                        }
                    ),
                )
                raise InvalidExpectation(
                    "Invalid specifications file: {}".format(modname)
                )

        raise UnsupportedExpectation("Unsupported expectations specification file")

    def generate(self, df):

        """
        Render a specified template using the context

        Args:
           df: Dataframe to profiled

        Returns:
            Rendered html template that can be embedded

        """
        if self.mode != "generate":
            raise InvalidExpectation("Mode is not generate")

        pass

    def validate(self, df, selector=None):
        """
        Run the loaded expectations

        Args:
           df: Dataframe to evaluated
           selector: Function to select the

        Returns:
           result: A list of dictionaries, each has evaluation result
        """

        if self.mode != "validation":
            raise InvalidExpectation("Dataframe validation not enabled")

        mgr = ExpectationManagerBase()
        mgr.initialize()

        expectations = self.expectations
        if callable(selector):
            expectations = selector(expectations)

        result = mgr.validate(df, expectations)

        try:
            json.dumps(result)
        except:
            logger.exception(
                "Error while processing expectations",
                extra={"transform": self.transform.name},
            )
            return []

        return result
