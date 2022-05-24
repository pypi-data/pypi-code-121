import os
import sys
import copy
import json
import time
import numpy as np
from enrichsdk import Sink
import pandas as pd
from pandas.io import sql
import logging

from enrichsdk.lib.misc import *
from enrichsdk.core.frames import PandasDataFrame

logger = logging.getLogger("app")


class PQExport(Sink):
    """
    Parquet export for dataframes.

    The configuration requires a list of exports, each of which
    specifies a pattern for the frame name::

         'conf': {
            'args': {
                "exports": [
                  {
                      "name": "%(frame)s_pq",
                      "type": "pq", # optional. Default is pq
                      "frames": ["cars"],
                      "filename": "%(output)s/%(runid)s/%(frame)s.pq",
                      "params": {
                          # parquet parameters.
                          # "compression": 'gzip'
                          # "engine": 'auto'
                          # "index" :None,
                          # "partition_cols": None
                      }
                   }
                ]
            }
        }

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "PQExport"
        self.roles_supported = ["Export"]
        self.roles_current = "Export"

        data_root = os.path.join(os.environ["ENRICH_TEST"], self.name)
        self.testdata = {
            "data_root": data_root,
            "outputdir": os.path.join(data_root, "runs"),
            "inputdir": os.path.join(os.environ["ENRICH_TEST"]),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {
                "args": {
                    "exports": [
                        {
                            "name": "%(frame)s_pq",
                            # "type": "pq",
                            "frames": ["cars"],
                            "filename": "%(output)s/%(runid)s/%(frame)s.pq",
                            "sample": True,
                            "params": {
                                # "compression": 'gzip'
                                # "engine": 'auto'
                                # "index" :None,
                                # "partition_cols": None
                            },
                        }
                    ]
                }
            },
            "data": {
                "cars": {
                    "transform": "CarSales",
                    "filename": "sales.csv",
                    "params": {"sep": ","},
                }
            },
        }

    def preload_clean_args(self, args):
        """ """
        args = super().preload_clean_args(args)

        if len(args) == 0:
            raise Exception("Empty args provided")

        if ("exports" not in args) or (not isinstance(args["exports"], list)):
            raise Exception("PQExport requires a series of exports (a list)")

        for e in args["exports"]:

            if (
                (not isinstance(e, dict))
                or ("filename" not in e)
                or ("name" not in e)
                or ("frames" not in e)
            ):
                raise Exception(
                    "Each element of the export should be a dictionary with filename, type, and frames"
                )

            if e.get("type", "pq") not in ["pq"]:
                raise Exception("Only parquet exports are supported in current version")

        return args

    def process(self, state):
        """
        Export frames as parquet files as shown in the example.
        """

        # Sanity check...
        for e in self.args["exports"]:

            namebase = e["name"]
            params = e.get("params", {})
            sample = e.get("sample", True)

            # Collect all the frames data
            for f in e["frames"]:

                detail = state.get_frame(f)
                if detail is None:
                    raise Exception("Frame not present in state: {}".format(f))

                if detail["frametype"] != "pandas":
                    raise Exception("Frame not a pandas dataframe: {}".format(f))
                    continue

                df = detail["df"]

                # Resolve the locations
                filename = os.path.abspath(
                    self.config.get_file(e["filename"], extra={"frame": f})
                )
                relpath = self.config.get_relative_path(
                    filename, what="enrich_data_dir"
                )

                # Check over-rides
                overrides = self.frame_get_overrides(detail)
                save = overrides.get("save", True)
                if save:
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except:
                        pass
                    df.to_parquet(filename, **params)

                    if sample:
                        size = min(1000, df.shape[0])
                        df.sample(size).to_parquet(filename + ".sample", **params)

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

                if not os.path.exists(filename):
                    logger.error(
                        "PQ file not created or missing",
                        extra=self.config.get_extra(
                            {
                                "transform": self.name,
                                "data": "Filename: {}\nOverride Present: {}".format(
                                    filename, override_present
                                ),
                            }
                        ),
                    )
                    raise Exception("PQ file missing")

                # => Create state detail
                state_detail = {
                    "df": None,
                    "frametype": "db",
                    "transform": self.name,
                    "params": [
                        {
                            "filename": filename,
                            "action": "output",
                            "frametype": "binary",
                            "columns": self.collapse_columns(detail),
                            "descriptions": ["Parquet export of {} frame".format(f)],
                            "components": [
                                {
                                    "filename": relpath,
                                    "type": "pq",
                                    "rows": df.shape[0],
                                    "columns": df.shape[1],
                                    "sha256sum": get_checksum(filename),
                                    "filesize": "{0:0.1f} MB".format(
                                        get_file_size(filename) / (1024 * 1024)
                                    ),
                                    "modified_time": str(
                                        time.ctime(os.path.getmtime(filename))
                                    ),
                                    "create_time": str(
                                        time.ctime(os.path.getctime(filename))
                                    ),
                                }
                            ],
                        },
                        {
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
                    ],
                    "history": [{"transform": self.name, "log": "Write PQite export"}],
                }
                try:
                    name = namebase % {"frame": f}
                    state.update_frame(name, state_detail, create=True)
                    state.make_note("Generated PQ export for {}".format(f))
                except:
                    logger.exception(
                        "Unable to store state",
                        extra=self.config.get_extra({"transform": self.name}),
                    )
                    raise Exception("Error while storing")

    def validate_results(self, what, state):
        """ """
        exports = self.args["exports"]
        for e in exports:
            namebase = e["name"]
            frames = e["frames"]
            for f in frames:
                name = namebase % {"frame": f}
                detail = state.get_frame(name)
                assert detail is not None


provider = PQExport
