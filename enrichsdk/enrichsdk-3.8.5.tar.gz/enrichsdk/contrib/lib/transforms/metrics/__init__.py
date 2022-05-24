import os
import sys
import json
import yaml
import copy
import tempfile
import shutil
import time
import glob
import re
import traceback
import subprocess
import numpy as np
import pandas as pd
from enrichsdk import Compute, S3Mixin
from datetime import datetime, date, timedelta
from dateutil import parser as dateparser, relativedelta
import logging
from sqlalchemy import create_engine, text as satext
from functools import partial

logger = logging.getLogger("app")

from enrichsdk.utils import get_lineage_of_query
from enrichsdk.lib.exceptions import NoDataFound


def note(df, title):
    msg = title + "\n"
    msg += "--------" + "\n"
    msg += "Timestamp: " + str(datetime.now()) + "\n"
    msg += "\nShape: " + str(df.shape) + "\n"
    msg += "\nColumns: " + ", ".join(df.columns) + "\n"
    if len(df) > 0:
        msg += "\nSample:" + "\n"
        msg += df.sample(min(2, len(df))).T.to_string() + "\n" + "\n"
    msg += "\nDtypes" + "\n"
    msg += df.dtypes.to_string() + "\n"
    msg += "------" + "\n"
    return msg


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except:
            return str(obj)


def get_yesterday():
    yesterday = date.today() + timedelta(days=-1)
    return yesterday.isoformat()


def get_today():
    return date.today().isoformat()


class MetricsBase(Compute):
    """
    Compute metrics as input for the anomaly/other computation

    Features of transform baseclass include:

        * Flexible configuration
        * Highlevel specification of dimensions and metrics

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "MetricsBase"
        self.description = "Compute metrics against datasources"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

    @classmethod
    def instantiable(cls):
        return False

    def get_printable_db_uri(self, engine):
        """
        pretty print the URL
        """
        username = engine.url.username
        host = engine.url.host
        database = engine.url.database
        drivername = engine.url.get_driver_name()

        return f"{drivername}:///{host}/{database}/"

    def get_db_uri(self, source):
        """
        Return database URI for a source
        """
        return source["uri"]

    def get_handlers(self, profile):
        """
        Define various callbacks that take a dataframe, spec
        and compute. Specific to a single profile.
        """
        return {}

    def get_profile(self):
        """
        Read the profile json
        """

        if (not hasattr(self, "profiledir")) and (not hasattr(self, "profilefile")):
            raise Exception(
                "'profiledir' transform attribute should be defined to use default get_profile method"
            )

        paths = []
        if hasattr(self, "profilefile"):
            paths.append(self.profilefile)

        if hasattr(self, "profiledir"):
            paths.extend(
                [
                    self.profiledir + "/profile.json",
                    self.profiledir + "/profile.yaml",
                    self.profiledir + "/profilespec.json",
                    self.profiledir + "/profilespec.yaml",
                ]
            )

        profile = None
        for p in paths:
            if not os.path.exists(p):
                continue
            if p.endswith(".json"):
                profile = json.load(open(p))
            elif p.endswith(".yaml"):
                profile = yaml.load(open(p))

        if profile is None:
            raise Exception("Profile could not be found")

        sources = profile["sources"]
        specs = profile["specs"]
        logger.debug(
            f"Found {len(sources)} sources {len(specs)} specs",
            extra={"transform": self.name, "data": json.dumps(profile, indent=4)},
        )

        return profile

    def get_specs(self, profile):
        if (not isinstance(profile, dict)) or ("specs" not in profile):
            raise Exception("Specs not defined in profile")
        return profile["specs"]

    def get_sources(self, profile):
        if (not isinstance(profile, dict)) or ("sources" not in profile):
            raise Exception("Sources not defined in profile")
        return profile["sources"]

    def get_db_query(self, source):

        # Generate/extract the query...
        query = source["query"]
        if callable(query):
            query = quer(source)
        return query

    def update_frame(self, source, df, lineage=None):

        if isinstance(source, str):
            name = source
            description = ""
        else:
            name = source["name"]
            description = source.get("description", "")

        if self.state.has_frame(name):
            return

        params = self.get_column_params(name, df)
        if lineage is not None:
            if isinstance(lineage, dict):
                params.append(lineage)
            else:
                params.extend(lineage)

        detail = {
            "name": name,
            "df": df,
            "frametype": "pandas",
            "description": description,
            "params": params,
            "transform": self.name,
            "history": [],
        }

        self.state.update_frame(name, detail)

    def read_db_source(self, source):

        # Get the SQLAlchemy URI
        uri = self.get_db_uri(source)

        # Get the query
        query = self.get_db_query(source)

        # Create the engine
        engine = create_engine(uri)

        # Run the query
        df = pd.read_sql_query(satext(query), con=engine)

        # Now the input load...
        lineage = {
            "type": "lineage",
            "transform": self.name,
            "dependencies": [
                {
                    "type": "database",
                    "nature": "input",
                    "objects": [self.get_printable_db_uri(uri)],
                },
            ],
        }

        self.update_frame(source, df, lineage)

        return df

    def get_datasets(self, profile, specs):
        """
        Load the datasets specified by the profile
        """

        if not isinstance(profile, dict) or len(profile) == 0:
            logger.warning("Empty profile", extra={"transform": self.name})
            return {}

        # Get various kinds of handlers..
        handlers = self.get_handlers(profile)
        if not isinstance(handlers, dict) or len(handlers) == 0:
            logger.warning("No handlers specified", extra={"transform": self.name})
            handlers = {}

        required_sources = []
        for s in specs:
            required_sources.extend(s["sources"])
        required_sources = list(set(required_sources))

        # Now no about constructucting the datasets
        datasets = {}

        sources = self.get_sources(profile)
        for source in sources:

            nature = source.get("nature", "db")
            name = source["name"]

            if name not in required_sources:
                continue

            pipeline = source.get("pipeline", None)
            generate = source.get("generate", None)

            # Only db is used for now...
            try:
                if nature == "db":
                    result = self.read_db_source(source)
                elif (
                    (generate is not None)
                    and (generate in handlers)
                    and (callable(handlers[generate]))
                ):
                    result = handlers[generate](source)
                elif (generate is not None) and (hasattr(self, generate)):
                    result = getattr(self, generate)(source)
                else:
                    raise Exception(f"Invalid specification: {name}")
            except:
                logger.exception(
                    f"[{name}] generation failed", extra={"transform": self.name}
                )
                continue

            # Clean the read the dataset...
            try:
                if pipeline is not None and isinstance(pipeline, list):
                    for processor in pipeline:
                        if isinstance(processor, str):
                            if processor in handlers:
                                result = handlers[processor](result, source)
                            elif hasattr(self, processor):
                                result = getattr(self, processor)(result, source)
                            else:
                                raise Exception(f"Missing post-processor: {processor}")
                        elif callable(processor):
                            result = processor(result, source)
                        else:
                            raise Exception(
                                "Only method names/callables are supported are supported"
                            )
            except:
                logger.exception(
                    f"[{name}] post-processing failed", extra={"transform": self.name}
                )
                continue

            # We could return multiple values or a single value
            if isinstance(result, dict):
                datasets.update(result)
            else:
                datasets[name] = df

        return datasets

    def get_spec_sources(self, spec, datasets):

        name = spec["name"]

        if ("sources" not in spec) and ("source" not in spec):
            raise Exception(f"[{name}] Invalid specification. Missing dataset")

        sources = spec.get("sources", spec.get("source"))
        if isinstance(sources, str):
            sources = [sources]

        policy = spec.get("missing", "fail")
        for s in sources:
            if s not in datasets:
                if policy == "fail":
                    raise Exception(f"[{name}] Missing source: {s}")

        return {s: datasets[s] for s in sources if s in datasets}

    def process_spec(self, datasets, profile, spec):

        if ("name" not in spec) or ("description" not in spec):
            raise Exception("Invalid spec: name/description missing")

        name = spec["name"]
        handlers = self.get_handlers(profile)

        if (not isinstance(spec, dict)) or (len(spec) == 0):
            raise Exception("Spec should be a dict")

        if "generate" not in spec:
            # It is database operational specification..
            data = self.process_spec_default(datasets, profile, spec)
        else:
            # Custom callback
            data = self.process_spec_custom(datasets, profile, spec)

        # The spec processor can return multiple dataframes
        if isinstance(data, pd.DataFrame):
            data = {name: data}

        pipeline = spec.get("pipeline", None)
        if pipeline is not None:
            for processor in pipeline:
                if isinstance(processor, str):
                    if processor in handlers:
                        data = handlers[processor](data, spec)
                    elif hasattr(self, processor):
                        data = getattr(self, processor)(data, spec)
                    else:
                        raise Exception(f"Missing cleaner: {processor}")
                elif callable(processor):
                    data = processor(data, spec)
                else:
                    raise Exception(
                        "Only method names/callables are supported are supported"
                    )

        return

    def process_spec_custom(self, datasets, profile, spec):

        name = spec["name"]
        handlers = self.get_handlers(profile)

        # Custom...
        generate = spec["generate"]
        callback = None
        if (generate in handlers) and (not callable(handlers[generate])):
            callback = handlers[generate]
        elif hasattr(self, generate):
            callback = getattr(self, generate)

        if callback is None:
            raise Exception(f"[{name}] Invalid callback: {generate}")

        # Get hold of the data first...
        sources = self.get_spec_sources(spec, datasets)

        return callback(sources, spec)

    def process_spec_default(self, datasets, profile, spec):
        """
        Handle one specification at a time..
        """

        if ("dimensions" not in spec) or (not isinstance(spec["dimensions"], dict)):
            raise Exception("Dimensions in spec should be a dict")

        if ("metrics" not in spec) or (not isinstance(spec["metrics"], dict)):
            raise Exception("Metrics in spec should be a dict")

        # Get hold of the data first...
        sources = self.get_spec_sources(spec, datasets)

        if len(sources) > 1:
            raise Exception("Use custom spec handler for multiple sources")

        datasetdf = list(sources.values())[0]

        # now go through each of the dimensions
        dimensions = spec["dimensions"]
        metrics = spec["metrics"]

        _dfs = []
        for name, cols in dimensions.items():

            if isinstance(cols, str):
                cols = [cols]

            # Dont need to include other columns...
            relevant = cols + list(metrics.keys())
            df = datasetdf[relevant]

            # Check if there are lists and explode them...
            for col in cols:
                if isinstance(df.iloc[0][col], list):
                    df = df.explode(col)

            # Construct aggregates...
            df = df.groupby(cols)
            df = df.agg(metrics)

            # Clean up the index if multiple columns are specified
            if len(cols) > 1:
                df.index = df.index.map("+".join)
            df.index.name = "value"
            df = df.reset_index()

            # Also cleanup the column names...
            def clean_colname(what):
                if isinstance(what, (list, tuple)):
                    what = "_".join(what)
                    what = what.rstrip("_").lstrip("_")
                return what

            df.columns = df.columns.map(clean_colname)

            df.insert(0, "dimensions", name)

            _dfs.append(df)

        # merge all
        df = pd.concat(_dfs)
        del _dfs

        return {spec["name"]: df}

    def get_dataset_generic(self, source):
        """
        Use the dataset object to read the dataset
        """

        if (not hasattr(self, "read_data")) or (not hasattr(self, "get_dataset")):
            raise Exception(
                " get_dataset_raw expects read_data and get_dataset methods"
            )

        args = self.args

        start_date = source.get('start_date', self.args["start_date"])
        end_date = source.get('end_date', self.args["end_date"])

        name = source["name"]
        dataset = source["dataset"]
        params = source.get("params", {})

        cache = args.get("cache", False)
        cachename = f"{dataset}-{start_date}-{end_date}"
        cachefile = f"cache/{self.name}-cache-" + cachename + ".csv"

        if cache:
            try:
                os.makedirs(os.path.dirname(cachefile))
            except:
                pass
            if os.path.exists(cachefile):
                logger.debug(
                    "Read cached {}".format(name), extra={"transform": self.name}
                )

                df = pd.read_csv(cachefile, **params)
                return {name: df}

        datasetobj = self.get_dataset(dataset)

        df, metadata = datasetobj.read_data(
            start_date,
            end_date,
            filename=source["filename"],
            readfunc=self.read_data,
            params=params,
        )

        logger.debug("Read {}".format(name), extra={"transform": self.name})

        # Cache it for future use...
        if cache:
            df.to_csv(cachefile, index=False)

        # Insert lineage if possible
        lineage = None
        if ("files" in metadata) and (len(metadata["files"]) > 0):
            lineage = {
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "file",
                        "nature": "input",
                        "objects": [metadata["files"][-1]],
                    },
                ],
            }

        self.update_frame(source, df, lineage)

        return {name: df}

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        profile = self.get_profile()

        # Get specs..
        specs = self.get_specs(profile)

        # First get the datasets
        datasets = self.get_datasets(profile, specs)

        # Now go through each spec and get the output..
        for spec in specs:
            enable = spec.get("enable", True)
            if not enable:
                continue
            self.process_spec(datasets, profile, spec)

        # Done
        logger.debug(
            "Complete execution", extra=self.config.get_extra({"transform": self.name})
        )

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        pass
