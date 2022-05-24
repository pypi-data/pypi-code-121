import os
import sys
import json
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

logger = logging.getLogger("app")

from enrichsdk.utils import get_lineage_of_query


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


class InMemoryQueryExecutorBase(Compute):
    """
    Base class for an InMemory QueryExecutor transform. This is useful
    to run queries against backends such as backends such as
    mysql

    Features of transform baseclass include:

        * Support multiple query engines (via SQLAlchemy)
        * Support templatized execution
        * Support arbitrary number of queries
        * Supports a generator function to generate per-interval queries

    Configuration looks like::

        ...
        "args": {
            "cleanup": False,
            "force": True,
            "targets": "all",
            "start_date": "2020-08-01",
            "end_date": "2020-08-03",
        }

     Specs

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "QueryExecutorBase"
        self.description = "Execute queries against backends"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

    @classmethod
    def instantiable(cls):
        return False

    def preload_clean_args(self, args):
        """
        Check validity of the args
        """
        args = super().preload_clean_args(args)

        if ("start_date" not in args) or ("end_date" not in args):
            raise Exception("Start or end of timeframe missing")

        try:
            start = dateparser.parse(args["start_date"]).date()
            args["start_date"] = start
            end = dateparser.parse(args["end_date"]).date()
            args["end_date"] = end
        except:
            logger.exception(
                "Invalid start_date or end_date", extra={"transform": self.name}
            )
            raise Exception("Invalid start/end datetime specified")

        if (
            ("targets" not in args)
            or (not isinstance(args["targets"], str))
            or (len(args["targets"]) == 0)
        ):
            raise Exception("Invalid list of query names specified")

        # Include force
        force = str(args["force"]).lower().strip()
        force = force == "true"
        args["force"] = force

        # Clean the list of names...
        targets = args["targets"].split(",")
        targets = [n.strip() for n in targets if len(n.strip()) > 0]
        args["targets"] = [n for n in targets if len(n) > 0]

        return args

    def get_supported_extra_args(self):
        """
        Look at the specs to generate a list of options that
        can be presented to the end-ser
        """

        # Collect specs first..
        specs = self.get_sql_specs()

        # Compute the targets
        targets = ["all"]  # default
        for s in specs:
            if not s.get("enable", True):
                continue
            categories = s.get("categories", [])
            for c in categories:
                if c not in targets:
                    targets.append(c)
        for s in specs:
            name = s["name"]
            if name not in targets:
                targets.append(name)
        targets = "|".join(targets)

        # Now construct the args dynamically
        remaining = self.supported_extra_args
        return [
            {
                "name": "targets",
                "description": f"What all to run. Specify multiple with comma separating names ({targets})",
                "default": "all",
                "required": False,
            },
            {
                "name": "force",
                "description": "Force execution",
                "default": "False",
                "required": False,
            },
            {
                "name": "start_date",
                "description": "Start of the time window",
                "default": get_yesterday(),
                "required": True,
            },
            {
                "name": "end_date",
                "description": "End of the time window",
                "default": get_today(),
                "required": True,
            },
        ] + remaining

    def update_frame(self, name, engine, sql, df, dependencies=[]):
        """
        Note the lineage for each output file.
        """

        # Check if it has already been registered
        if self.state.has_frame(name):
            return

        # Get the default database
        database = engine.url.database

        # Insert extra dependencies
        dependencies += get_lineage_of_query(engine, sql)

        lineage = {"type": "lineage", "dependencies": dependencies}

        # Generate column information...
        columns = self.get_column_metadata(name, df)

        ## => Gather the update parameters
        updated_detail = {
            "df": None,
            "description": f"Output for query {name}",
            "transform": self.name,
            "frametype": "pandas",
            "params": [
                {
                    "type": "compute",
                    "columns": columns,
                },
                lineage,
            ],
        }

        # Dump it into the shared state
        self.state.update_frame(name, updated_detail, create=True)

    def generate_paramsets(self, spec, start_date, end_date):

        duration = spec.get("paramsets_duration", "full")
        window = spec.get("paramsets_window", 0)

        if isinstance(start_date, str):
            start_date = parser.parse(start_date).date()

        if isinstance(end_date, str):
            end_date = parser.parse(end_date).date()

        if duration not in ["day", "full"]:
            raise Exception("Only day and full are supported. full is default")

        if duration == "full":
            return [
                {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "start_date_minus7": (
                        start_date + relativedelta.relativedelta(days=-7)
                    ).isoformat(),
                    "start_date_minus1": (
                        start_date + relativedelta.relativedelta(days=-1)
                    ).isoformat(),
                    "start_date_minus6_months": (
                        start_date + relativedelta.relativedelta(months=-6)
                    ).isoformat(),
                    "end_date_plus1": (
                        end_date + relativedelta.relativedelta(days=1)
                    ).isoformat(),
                    "end_date_minus1": (
                        end_date + relativedelta.relativedelta(days=-1)
                    ).isoformat(),
                    "end_date_minus7": (
                        end_date + relativedelta.relativedelta(days=-7)
                    ).isoformat(),
                    "end_date_minus6_months": (
                        end_date + relativedelta.relativedelta(months=-6)
                    ).isoformat(),
                }
            ]

        # There may be more. So leaving it here...
        if duration == "day":

            # Parse the dates
            if start_date > end_date:
                start_date, end_date = end_date, start_date

            # Sanity check
            diff = end_date - start_date
            if diff.days > 100:
                raise Exception("Date range should be < 100 days")

            # Generate one for each day
            paramsets = []
            curr_date = start_date
            while curr_date <= end_date:
                paramsets.append(
                    {
                        "start_date": curr_date.isoformat(),
                        "end_date": (
                            curr_date + relativedelta.relativedelta(days=window)
                        ).isoformat(),
                        "start_date_minus7": (
                            curr_date + relativedelta.relativedelta(days=-7)
                        ).isoformat(),
                        "start_date_minus1": (
                            curr_date + relativedelta.relativedelta(days=-1)
                        ).isoformat(),
                        "start_date_plus1": (
                            curr_date + relativedelta.relativedelta(days=1)
                        ).isoformat(),
                        "end_date_minus1": (
                            curr_date + relativedelta.relativedelta(days=-1)
                        ).isoformat(),
                        "end_date_plus1": (
                            curr_date + relativedelta.relativedelta(days=1)
                        ).isoformat(),
                        "end_date_minus7": (
                            curr_date + relativedelta.relativedelta(days=-7)
                        ).isoformat(),
                        "end_date_minus6_months": (
                            curr_date + relativedelta.relativedelta(months=-6)
                        ).isoformat(),
                    }
                )
                curr_date += relativedelta.relativedelta(days=1)

            return paramsets

        # Default...
        raise Exception(f"Unknown duration: {duration}")

    def get_sql_specs(self):
        """
        Return a list of query specifications.

        Specification: A list of dictionaries. Each dict has

          * name: Name of the specification
          * sql: SQL template
          * categories: String or a list of strings indicating specification groups
          * segment: How to split the dataframe resulting from query execution. Could be none ('complete' as the default name), string (column name) or a callback that generates a { name: df } map
          * paramsets_duration: each instance for one 'day' or a window of days (defined below)
          * paramsets_window: each instance translates into date range for each instance of parameters.

        Examples::

           Simple:
             {
                 "name": "txn_value",
                 "sql": "txn_value.sql",
                 "segment": "global_date",
             }

           Simple:

             {
                 "categories": ["kyc"],
                 "name": "kyc_txn_summary",
                 "sql": "kyc_txn_summary.sql",
                 "segment": complex_split_callbak,
                 "paramsets_duration": "day",
                 "retries": 3,
             },

        """

        self.get_specs()

    def get_specs(self):
        """
        Use get_sql_specs instead.

        .. warning::
            .. deprecated:: 2.6.0

        """

        return []

    def get_registry(self):
        """
        Build a registry and return
        """
        return None

    def get_engine(self, spec):
        """
        Build and return an engine for a given specification.
        """
        raise Exception("Construct sqlalchemy engine")

    def generic_clean(self, df):
        """
        Do a high level clean of the query result before
        doing a query-specific clean
        """
        return df

    def get_specs_from_sqls(self, sqldir):
        """
        Helper function. Load specifications from the SQLs.
        """
        specs = []

        files = glob.glob(sqldir + "/*.sql")
        for f in files:
            name = os.path.basename(f).replace(".sql", "")
            sql = open(f).read()

            # Specify the split in the SQL itself..
            segment = None
            match = re.search(r"-- segment:: (\S+)", sql)
            if match is not None:
                segment = match.group(1).strip()

            match = re.search(r"-- name:: (\S+)", sql)
            if match is not None:
                name = match.group(1).strip()

            match = re.search(r"-- engine:: (\S+)", sql)
            if match is not None:
                engine = match.group(1).strip()

            specs.append(
                {"name": name, "sql": sql, "segment": segment, "engine": engine}
            )

        return specs

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # Get the registry
        self.registry = self.get_registry()

        # List of specification names
        targets = self.args["targets"]

        # Get specs..
        specs = self.get_sql_specs()

        logger.debug(f"Specs found: {len(specs)}", extra={"transform": self.name})
        # Now iterate through the specs.
        for spec in specs:
            try:

                name = spec["name"]
                categories = spec.get("categories", ["all"])
                table = spec.get("table", name)
                cond = spec.get("cond", "")
                retries = spec.get("retries", 1)

                # To take care of the logging in case of exception
                msg = f"Name: {name}\n"

                # Check if this has been requested?
                if all([c not in targets for c in categories]) and (
                    name not in targets
                ):
                    continue

                logger.debug(
                    f"Executing {spec['name']}",
                    extra={
                        "transform": self.name,
                        "data": json.dumps(spec, indent=4, cls=CustomEncoder),
                    },
                )

                sql_template = spec["sql"]

                files = []

                paramsets = self.generate_paramsets(
                    spec, self.args["start_date"], self.args["end_date"]
                )

                for params in paramsets:

                    status = []

                    msg = f"Params: {params}\n"
                    msg += f"Insert Table: {table} with {cond}\n"

                    # Now log the SQL
                    sql = sql_template % params
                    msg += "SQL:\n{}\n".format(sql)

                    # Get the engine for a given spec
                    engine = self.get_engine(spec)

                    segmentcol = spec.get("segment", None)

                    tryno = 1
                    while True:
                        if tryno > retries:
                            raise Exception("Exceeded max retries")

                        try:
                            df = pd.read_sql(sql, engine)
                            break
                        except:
                            logger.exception(
                                f"Failed Query: {name} (try {tryno})",
                                extra={"transform": self.name, "data": msg},
                            )
                        tryno += 1
                        time.sleep(30)

                    # Do some basic cleaning. int becomes float
                    df = self.generic_clean(df)

                    msg += f"Segment: {segmentcol} (Initial split)\n"
                    msg += "Records: {}\n".format(df.shape[0])
                    msg += "Columns: {}\n".format(", ".join(df.columns))
                    msg += "Dtypes: " + df.dtypes.to_string() + "\n"

                    if len(df) == 0:
                        # no data returned...
                        logger.warning(
                            f"Completed {name} {params['start_date']} No data",
                            extra={"transform": self.name, "data": msg},
                        )
                        continue

                    # First gather a map of segments
                    filemap = {}
                    if segmentcol is None:
                        # Whole thing is one segment
                        filemap["complete"] = df
                    elif isinstance(segmentcol, str):
                        # Split by column name...
                        segments = list(df[segmentcol].unique())
                        msg += f"Segments: {len(segments)} ({segmentcol})\n"
                        for segment in segments:
                            try:
                                df1 = df[df[segmentcol] == segment]
                                segment = str(segment)
                                filemap[segment] = df1
                            except:
                                pass
                    elif callable(segmentcol):
                        # Custom split of the dataframe...
                        filemap = segmentcol(self, spec, params, df)
                        msg += f"Segments: {len(filemap)}\n"
                    else:
                        raise Exception(f"Unhandled segment definition: {segmentcol}")

                    # => Process each segment obtained from
                    # the previous step...
                    for segment, df1 in sorted(filemap.items()):

                        # Add note about what is being stored..
                        msg += f"[{segment}] {df1.shape[0]} records\n"

                        # Clean the output data...
                        try:
                            if "clean" in spec:
                                callback = spec["clean"]["callback"]
                                if callable(callback):
                                    clean_msg, df1, clean_files = callback(
                                        self, segmentcol, segment, df1, spec
                                    )
                                    if len(clean_msg) > 0:
                                        msg += f"[{segment}] " + clean_msg + "\n"
                                    files += clean_files
                        except Exception as e:
                            #traceback.print_exc()
                            msg += str(e)
                            raise

                        # Store in database...
                        try:
                            extra_dependencies = []
                            if "store" in spec:
                                # Separate storage handler..
                                callback = spec["store"]["callback"]
                                if callable(callback):
                                    store_msg, store_dependencies, store_files = callback(
                                        self, segmentcol, segment, df1, spec
                                    )
                                    if len(store_msg) > 0:
                                        msg += f"[{segment}] " + store_msg + "\n"
                                    extra_dependencies += store_dependencies
                                    files += store_files

                        except Exception as e:
                            #traceback.print_exc()
                            msg += str(e)
                            raise

                        # Handle a default store for all specs, segments
                        try:

                            # Store in s3 etc.
                            store_msg, store_dependencies, store_files  = self.store(
                                segmentcol, segment, df1, spec
                            )
                            if len(store_msg) > 0:
                                msg += f"[{segment}] " + store_msg
                            extra_dependencies += store_dependencies
                            files += store_files

                            # update lineage
                            self.update_frame(
                                name, engine, sql, df1, extra_dependencies
                            )

                        except Exception as e:
                            #traceback.print_exc()
                            msg += "[{}] Exception {}\n".format(segment, str(e))

                    logger.debug(
                        f"Completed {name} {params['start_date']}",
                        extra={"transform": self.name, "data": msg},
                    )

                # Make note of it.
                dataset = self.registry.find(spec['name'])
                if ((dataset is not None) and (len(files) > 0)):
                    metadata = { 'files': files}
                    self.registry.access(dataset, metadata, nature='write')

            except:
                #traceback.print_exc()
                # Exception for each spec.
                logger.exception(
                    f"Unable to run query: {name}",
                    extra={"transform": self.name, "data": msg},
                )
                msg = ""
                continue

        self.add_marker(state)

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
