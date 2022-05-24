import os
import sys
import json
import re
import copy
from enrichsdk import Sink
import logging

logger = logging.getLogger("app")


class JSONSink(Sink):
    """
    Store a 'dict' frame that is present in the state into a file.

    Params are meant to be passed as parameter to update_frame.

    Example configuration::

         "args": {
             "sink": {
                 'test': {
                     'frametype': 'dict',
                     'filename': '%(output)s/%(runid)s/mytestoutput.json',
                     'params': {}
                 }
             }
         }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "JSONSink"

        self.testdata = {
            "conf": {
                "args": {
                    "sink": {
                        "frame1": {
                            "frametype": "dict",
                            "filename": "%(output)s/%(runid)s/mytestoutput.json",
                            "params": {},
                        }
                    }
                }
            },
            "data": {
                "frame1": {
                    "filename": "outputjson.json",
                    "frametype": "dict",
                    "transform": "TestJSON",
                    "params": {},
                }
            },
        }

    def preload_clean_args(self, args):
        """
        Clean when the spec is loaded...
        """

        if "sink" not in args:
            args = {"sink": args}

        args = super().preload_clean_args(args)

        assert "sink" in args
        assert isinstance(args["sink"], dict)
        assert len(args["sink"]) > 0

        sink = args["sink"]
        for name, detail in sink.items():

            if ("frametype" not in detail) or (detail["frametype"] != "dict"):
                logger.error(
                    "Invalid configuration. Only JSON/Dictionaries are supported by this sink transform",
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

            detail["root"] = self.config.enrich_data_dir

            tags = detail.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            detail["tags"] = tags

            # => Materialize the path...
            detail["filename"] = self.config.get_file(
                detail["filename"], extra={"frame_name": name}
            )

        return args

    def validate_args(self, what, state):
        """
        An extra check on the arguments to make sure
        it is consistent with the specification
        """
        args = self.args
        assert "sink" in args
        assert isinstance(args["sink"], dict)
        assert len(args["sink"]) > 0

        sink = args["sink"]
        for name, detail in sink.items():
            assert ("frametype" in detail) and (detail["frametype"] == "dict")
            assert "filename" in detail
            assert "params" in detail

    def process(self, state):
        """
        Store the dictionary 'frames' in the state in files.
        """
        logger.debug(
            "{} - process".format(self.name),
            extra=self.config.get_extra({"transform": self.name}),
        )

        available_frames = state.get_frame_list()

        # => First construct input for the pandasframe
        extra = {}
        args_input = {}
        write_input = {}
        framecls = self.config.get_dataframe("dict")

        sink = self.args["sink"]
        for pattern in sink:
            # The pattern could be precise dataframe name or could be
            # regular expression.
            regex = re.compile("^{}$".format(pattern))
            frames = [
                m.group(0) for f in available_frames for m in [regex.search(f)] if m
            ]
            if len(frames) == 0:
                logger.warning("Pattern has not matched any frames: {}".format(pattern))
                continue

            for f in frames:

                # Get the details of this frame
                detail = state.get_frame(f)

                # Handle frametype
                frametype = detail["frametype"]
                if frametype != "dict":
                    logger.warning(
                        "Pattern has matched non-dict frame: {}".format(f),
                        extra=self.config.get_extra({"transform": self.name}),
                    )
                    continue

                # Now construct the output file name
                filename = sink[pattern]["filename"]
                filename = self.config.get_file(
                    filename, create_dir=True, extra={"frame_name": f}
                )

                extra[f] = {
                    "notes": self.collapse_notes(detail),
                    "descriptions": self.collapse_descriptions(detail),
                }

                params = sink[pattern].get("params", {})
                write_input[f] = {
                    "frametype": detail["frametype"],
                    "filename": filename,
                    "pattern": pattern,
                    "df": detail["df"],
                    "params": params,
                }

                args_input[f] = copy.copy(sink[pattern])
                args_input[f]["filename"] = filename

        framecls.write(args_input, write_input)

        for name in write_input:

            detail = write_input[name]

            # => Insert columns and tags
            pattern = detail["pattern"]
            detail["params"]["tags"] = sink[pattern]["tags"]

            # Incorporate columns, notes and description
            detail["params"].update(extra[name])

            detail["params"] = [
                detail["params"],
                {
                    "type": "lineage",
                    "transform": self.name,
                    "dependencies": [
                        {"type": "dataframe", "nature": "input", "objects": [name]},
                        {
                            "type": "file",
                            "nature": "output",
                            "objects": [detail["params"]["filename"]],
                        },
                    ],
                },
            ]

            # Insert additional detail
            detail["transform"] = self.name
            detail["history"] = [{"transform": self.name, "log": "Wrote output"}]

            state.update_frame(name, detail)

        logger.debug(
            "Finished writing data",
            extra=self.config.get_extra({"transform": self.name}),
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


provider = JSONSink
