import os
import sys
import json
from enrichsdk import Source
import logging

logger = logging.getLogger("app")


class JSONSource(Source):
    """
    Load a file into a 'dict' frame in the state.

    Params are meant to be passed as parameter to update_frame.

    Example configuration::

         ...

         "args": {
             "source": {
                 'hello': {
                     'frametype': 'dict',
                     'filename': '%(data_root)s/shared/hello.json',
                     'params': {}
                 }
             }
         }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "JSONSource"

        self.testdata = {
            "conf": {
                "args": {
                    "source": {
                        "hello": {
                            "filename": "%(data_root)s/shared/hello.json",
                            "frametype": "dict",
                            "params": {},
                        }
                    }
                }
            },
            "data": {},
        }

    def preload_clean_args(self, args):
        """
        Check if the args are consistent with the
        specification.
        """

        # Backward compatabilty
        if "source" not in args:
            args = {"source": args}

        args = super().preload_clean_args(args)

        # Sanity check...
        assert isinstance(args, dict)
        assert "source" in args
        assert isinstance(args["source"], dict)

        source = args["source"]
        for name, detail in source.items():

            if ("frametype" not in detail) or (detail["frametype"] != "dict"):
                logger.error(
                    "Invalid configuration. Only JSON source supported by this source transform",
                    extra=self.config.get_extra({"transform": self.name}),
                )
                raise Exception("Invalid configuration")

            if (
                ("filename" not in detail)
                or (not isinstance(detail["filename"], str))
                or ("params" not in detail)
                or (not isinstance(detail["params"], dict))
            ):
                logger.error(
                    "Invalid args. Filename (string) and params (dict) are required",
                    extra=self.config.get_extra({"transform": self.name}),
                )
                raise Exception("Invalid configuration")

            filename = detail["filename"]
            if not filename.lower().endswith(".json"):
                logger.error(
                    "Input file must a .json file",
                    extra=self.config.get_extra({"transform": self.name}),
                )
                raise Exception("Invalid configuration")

            # => Materialize the path...
            detail["filename"] = self.config.get_file(detail["filename"])

        return args

    def validate_args(self, what, state):
        """
        Double check the arguments
        """
        assert isinstance(self.args, dict)
        assert "source" in self.args
        assert isinstance(self.args["source"], dict)

        source = self.args["source"]
        for name, detail in source.items():
            assert ("frametype" in detail) and (detail["frametype"] == "dict")
            assert "filename" in detail
            assert "params" in detail

    def process(self, state):
        """
        Load the json files into 'dict' frames and store them in the state.
        """
        logger.debug(
            "{} - process".format(self.name),
            extra=self.config.get_extra({"transform": self.name}),
        )

        source = self.args["source"]
        for name, detail in source.items():

            filename = detail["filename"]
            data = json.load(open(filename))

            updated_detail = {
                "df": data,
                "transform": self.name,
                "frametype": "dict",
                "params": [
                    {
                        "type": "compute",
                    },
                    {
                        "type": "lineage",
                        "transform": self.name,
                        "dependencies": [
                            {"type": "file", "nature": "input", "objects": [filename]}
                        ],
                    },
                ],
                "history": [
                    # Add a log entry describing the change
                    {"transform": self.name, "log": "Loaded json file"}
                ],
            }

            # Update the state.
            state.update_frame(name, updated_detail, create=True)

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        """
        Check to make sure that the execution completed correctly
        """

        source = self.args["source"]
        for name, detail in source.items():
            if not state.reached_stage(name, self.name):
                raise Exception("Could not find new frame created for {}".format(name))

                detail = state.get_frame(name)
                df = detail["df"]

                # Check if it is a valid dictionary...
                assert isinstance(df, dict)


provider = JSONSource
