import os
import sys
import copy
import json
import time
import traceback
import logging
import subprocess
import tempfile
import sqlite3
import jsonschema
from functools import partial

import numpy as np
import pandas as pd
from pandas.io import sql

from enrichsdk import Sink
from enrichsdk.lib.misc import *
from enrichsdk.core.frames import PandasDataFrame

logger = logging.getLogger("app")


class SQLExport(Sink):
    """
    Export dataframes into the SQL database. Args specify what and how
    the export should happen.

    The transform args provides the specification:

          * exports: A list of files that must be exported. Each is a
            dictionary with the following elements:

              * name: Name of this export. Used for internal tracking and notifications.
              * filename: Output filename. Can refer to other global attributes such as `data_root`, `enrich_root_dir` etc
              * type: Type of the export. Only `sqlite` supported for now
              * frames: List of frames of the type `pandas` that should
                exported as part of this file

    Example::

        ....
        "transforms": {
            "enabled": [
               ...
               {
                 "transform": "SQLExport",
                  "args": {
                      "exports": [
                        {
                           "type": "sqlite",
                           "filename": "%(output)s/cars.sqlite",
                           "frames": ["cars", "alpha"]
                        },
                       ...
                      ]
                    },
                   ...
               }
            ...
           }
         }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SQLExport"
        self.description = "Export frames into SQLite/Other formats"
        self.roles_supported = ["Export"]
        self.roles_current = "Export"

        self.testdata = {
            "conf": {
                "args": {
                    "exports": [
                        {
                            "name": "customerinfo",
                            "filename": "%(output)s/%(runid)s/customerinfo.sqlite",
                            "type": "sqlite",
                            "frames": ["customerinfo"],
                        }
                    ]
                }
            },
            "data": {
                "customerinfo": {
                    "transform": "MemberLoyaltyMetadata",
                    "filename": "customerinfo.csv",
                    "params": {"sep": ",", "dtype": {"MEMBERSHIP_ID_SUFFIX": "str"}},
                }
            },
        }

    def preload_clean_args(self, args):
        """
        Enforce the args specification given in the
        example above
        """
        args = super().preload_clean_args(args)

        if len(args) == 0:
            raise Exception("Empty args provided")

        if ("exports" not in args) or (not isinstance(args["exports"], list)):
            raise Exception("SQLExport requires a series of exports (a list)")

        for e in args["exports"]:

            if (
                (not isinstance(e, dict))
                or ("filename" not in e)
                or ("name" not in e)
                or ("type" not in e)
                or ("frames" not in e)
            ):
                raise Exception(
                    "Each element of the export should be a dictionary with filename, type, and frames"
                )

            if ("replace" in e) and (not isinstance(e["replace"], bool)):
                raise Exception("replace is a boolean variable")

            if e["type"] != "sqlite":
                raise Exception("Only sqlite exports are supported in current version")

            e["filename"] = os.path.abspath(self.config.get_file(e["filename"]))
            e["relpath"] = os.path.relpath(e["filename"], self.config.data_root)

        return args

    def process(self, state):
        """
        Execute the export specification.
        """
        # Sanity check...
        for e in self.args["exports"]:

            # Collect all the frames data
            missing = []
            invalid = []
            frames = {}
            for f in e["frames"]:
                detail = state.get_frame(f)
                if detail is None:
                    missing.append(f)
                    continue

                if detail["frametype"] != "pandas":
                    invalid.append(f)
                    continue

                frames[f] = detail

            if len(missing) > 0 or len(invalid) > 0:
                logger.error(
                    "Unable to export frames",
                    extra=self.config.get_extra(
                        {
                            "transform": self.name,
                            "data": "Invalid: {}\nMissing: {}".format(invalid, missing),
                        }
                    ),
                )
                raise Exception("Error while exporting")

            filename = e["filename"]
            filename = os.path.abspath(self.config.get_file(filename))
            relpath = self.config.get_relative_path(filename, what="enrich_data_dir")

            name = e.get("name", os.path.basename(filename))
            replace = e.get("replace", False)

            try:
                os.makedirs(os.path.dirname(filename))
            except:
                pass

            # Creating a database file
            conn = sqlite3.connect(filename)
            c = conn.cursor()

            for f in frames:

                # => Write the frames
                overrides = self.frame_get_overrides(frames[f])
                override_present = len(overrides) > 0
                save = overrides.get("save", True)
                if save:
                    try:

                        # Status flag
                        failed = False

                        df = frames[f]["df"]

                        # Drop existing table if necessary...
                        if replace:
                            c.execute(f"DROP TABLE IF EXISTS {f}")

                        # => First create the table schema
                        ddl = pd.io.sql.get_schema(df, f)
                        c.execute(ddl)  # CREATE table

                        # => Dump the dataframe to a csv
                        fd, tmpfile = tempfile.mkstemp(prefix="sqlexport")
                        df.to_csv(tmpfile, header=False, index=False)

                        # => Load it into sqlite
                        cmd = [
                            "/usr/bin/sqlite3",
                            filename,
                            "-cmd",
                            ".separator ,",
                            ".import {} {}".format(tmpfile, f),
                        ]

                        process = subprocess.Popen(
                            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        out, err = process.communicate()
                        err = err.decode("utf-8")
                        out = out.decode("utf-8")

                        # Dump what we have seen
                        if len(err) > 0:
                            failed = True
                            logfunc = partial(
                                logger.error, "Unable to export {}".format(f)
                            )
                        else:
                            logfunc = partial(logger.debug, "Exported {}".format(f))
                        logfunc(
                            extra=self.config.get_extra(
                                {
                                    "transform": self.name,
                                    "data": "Filename:{}\nOutput\n-----\n{}\n\nErr\n----\n{}".format(
                                        filename, out, err
                                    ),
                                }
                            )
                        )

                        # => Update the state for this transform..
                        if not failed:
                            state.update_frame(
                                f,
                                {
                                    "df": frames[f]["df"],
                                    "frametype": frames[f]["frametype"],
                                    "transform": self.name,
                                    "history": [{"log": "Exported to SQLite"}],
                                    "params": {
                                        "type": "lineage",
                                        "transform": self.name,
                                        "dependencies": [
                                            {
                                                "type": "dataframe",
                                                "nature": "input",
                                                "objects": [f],
                                            },
                                            {
                                                "type": "file",
                                                "nature": "output",
                                                "objects": [filename],
                                            },
                                        ],
                                    },
                                },
                            )

                    except:
                        logger.exception(
                            "Unable to export dataframe {}".format(f),
                            extra=self.config.get_extra(
                                {
                                    "transform": self.name,
                                }
                            ),
                        )

                    # Cleanup...
                    try:
                        if os.path.exists(tmpfile):
                            os.remove(tmpfile)
                    except:
                        pass

                    # Dont proceed
                    if failed:
                        raise Exception("Error while exporting {}".format(f))

                else:
                    logger.warn(
                        "Did not save {} due to overrides".format(f),
                        extra=self.config.get_extra(
                            {
                                "transform": self.name,
                                "data": "Overrides: {}".format(overrides),
                            }
                        ),
                    )

            conn.close()
            if not os.path.exists(filename):
                logger.error(
                    "SQLite file not created or missing",
                    extra=self.config.get_extra(
                        {
                            "transform": self.name,
                            "data": "Filename: {}\nOverride Present: {}".format(
                                filename, override_present
                            ),
                        }
                    ),
                )
                raise Exception("SQLite file missing")

            # Now create the state entry
            detail = {
                "df": None,
                "frametype": "db",
                "transform": self.name,
                "params": {
                    "filename": filename,
                    "action": "output",
                    "frametype": "db",
                    "descriptions": [
                        "SQLite export of {} frames ({})".format(
                            len(frames), ",".join(frames)
                        )
                    ],
                    "notes": ["Frames included: {}".format(",".join(frames))],
                    "components": [
                        {
                            "filename": relpath,
                            "type": "sqlite",
                            "sha256sum": get_checksum(filename),
                            "filesize": "{0:0.3f} MB".format(
                                get_file_size(filename) / (1024 * 1024)
                            ),
                            "modified_time": str(
                                time.ctime(os.path.getmtime(filename))
                            ),
                            "create_time": str(time.ctime(os.path.getctime(filename))),
                        }
                    ],
                },
                "history": [{"transform": self.name, "log": "Write SQLite export"}],
            }
            try:
                state.update_frame(name, detail, create=True)
                state.make_note("Generated database export")
            except:
                logger.exception(
                    "Unable to store state",
                    extra=self.config.get_extra({"transform": self.name}),
                )
                raise Exception("Error while storing")

    def validate_results(self, what, state):
        """
        Check to make sure that the execution completed correctly
        """
        pass


provider = SQLExport
