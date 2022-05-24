import os
import sys
import json
import copy
import tempfile
import shutil
import subprocess
import numpy as np
import pandas as pd
from enrichsdk import Compute, S3Mixin
from datetime import datetime
from dateutil import parser as dateparser, relativedelta
import logging

logger = logging.getLogger("app")

from .lib import *


class FileBasedQueryExecutorBase(Compute):
    """
    Base class for a File-based QueryExecutor transform. This is useful
    to run queries against backends such as backends such as
    mysql

    Features of transform baseclass include:

        * Support query engines (MySQL, Hive, Presto)
        * Support templatized execution
        * Support arbitrary number of queries
        * Supports a generator function to generate per-interval queries

    Configuration looks like::

        ...
        "args": {
            "cleanup": False,
            "force": True,
            "names": "all",
            "start": "2020-08-01",
            "end": "2020-08-03",
        }

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "FileBasedQueryExecutorBase"
        self.description = "Execute queries against backends and store in files"
        self.supported_extra_args = [
            {
                "name": "names",
                "description": "names of the queries to execute",
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
                "name": "start",
                "description": "Start of the time window",
                "default": "",
                "required": True,
            },
            {
                "name": "end",
                "description": "End of the time window",
                "default": "",
                "required": True,
            },
        ]

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

        if ("start" not in args) or ("end" not in args):
            raise Exception("Start or end of timeframe missing")

        try:
            start = dateparser.parse(args["start"])
            args["start"] = start
            end = dateparser.parse(args["end"])
            args["end"] = end
        except:
            logger.exception("Invalid start or end", extra={"transform": self.name})
            raise Exception("Invalid start/end datetime specified")

        if (
            ("names" not in args)
            or (not isinstance(args["names"], str))
            or (len(args["names"]) == 0)
        ):
            raise Exception("Invalid list of query names specified")

        # Include force
        force = str(args["force"]).lower().strip()
        force = force == "true"
        args["force"] = force

        # Clean the list of names...
        names = args["names"].split(",")
        names = [n.strip() for n in names if len(n.strip()) > 0]
        args["names"] = [n for n in names if len(n) > 0]

        return args

    ########################################
    # Specification Handling...
    ########################################
    def get_spec(self):
        """
        Get query execution specification. Override this

        Returns:

           specs (list): A list of dictionaries. Each dictionary
                         specifies name, credentials, queries to run

        Example::

           return [
               {
                   "name": "roomdb",
                   "cred": "roomdb",
                   "queries": [
                       {
                           "name": "select_star",
                           "output": "%(data_root)s/shared/db/select_star/%(dt)s.tsv",
                           "sql": "%(transform_root)s/SQL/select_star.sql",
                           "params": {
                            "alpha": 22
                           }
                       }
                   ]
               },
               {
                   "enable": False,
                   "name": "hive",
                   "cred": "hiveserver",
                   "queries": [
                       {
                           "name": "employees",
                           "output": "%(data_root)s/shared/db/employee/%(dt)s.tsv",
                           "sql": "%(transform_root)s/SQL/employees.hql",
                       }
                   ]
               }
           ]

        """
        return []

    def validate_spec(self, spec):
        """
        Check whether specification is valid
        """

        if not isinstance(spec, list):
            raise Exception("Query specification should be a list")

        for specitem in spec:

            if not isinstance(specitem, dict):
                logger.error(
                    "Query specification items should be dicts",
                    extra={
                        "transform": self.name,
                        "data": "Found {}\n{}".format(str(type(specitem)), specitem),
                    },
                )
                raise Exception("Invalid specification")

            if "executor" in specitem:
                executor = specitem["executor"]
                if (not callable(executor)) and (
                    not (
                        (isinstance(executor, str))
                        and (len(executor) > 0)
                        and (not hasattr(self, executor))
                    )
                ):
                    raise Exception("Invalid executor specified: {}".format(executor))

            if "generator" in specitem:
                generator = specitem["generator"]
                if (not callable(generator)) and (
                    not (
                        (isinstance(generator, str))
                        and (len(generator) > 0)
                        and (not hasattr(self, generator))
                    )
                ):
                    raise Exception("Invalid generator specified: {}".format(generator))

            expected = ["name", "cred", "queries"]
            missing = [name for name in expected if name not in specitem]
            if len(missing) > 0:
                logger.error(
                    "Query specification items should have required elements",
                    extra={
                        "transform": self.name,
                        "data": "Missing {} in:\n{}".format(missing, specitem),
                    },
                )
                raise Exception("Invalid specification")

            # => check the cred
            try:
                cred = self.get_credentials(specitem["cred"])
            except:
                logger.exception(
                    "Unable to find credentials", extra={"transform": self.name}
                )
                raise Exception("Invalid specification")

            for q in specitem["queries"]:
                if (not isinstance(q, dict)) or (len(q) == 0):
                    logger.error(
                        "Empty or invalid query specification",
                        extra={"transform": self.name, "data": "Query: {}".format(q)},
                    )
                    raise Exception("Invalid specification")

                expected = ["name", "sql", "output"]
                missing = [name for name in expected if name not in q]
                if len(missing) > 0:
                    logger.error(
                        "Query specification items should have required elements",
                        extra={
                            "transform": self.name,
                            "data": "Missing {} in:\n{}".format(missing, specitem),
                        },
                    )
                    raise Exception("Invalid specification")

                if not isinstance(q["sql"], str) or len(q["sql"]) == 0:
                    logger.error(
                        "Query specification items has invalid sql",
                        extra={
                            "transform": self.name,
                            "data": "SQL: {}".format(q["sql"]),
                        },
                    )
                    raise Exception("Invalid specification")

                if "generator" in q:
                    generator = q["generator"]
                    if (not callable(generator)) and (
                        not (
                            (isinstance(generator, str))
                            and (len(generator) > 0)
                            and (not hasattr(self, generator))
                        )
                    ):
                        raise Exception(
                            "Invalid generator specified: {}".format(generator)
                        )

            if "definitions" in specitem:
                definitions = specitem["definitions"]
                if (not instance(definitions, dict)) or (len(definitions) == 0):
                    logger.error(
                        "Query specification items should have valid definition",
                        extra={
                            "transform": self.name,
                            "data": "Expected non-empty dict. Found:\n{}".format(
                                specitem
                            ),
                        },
                    )
                    raise Exception("Invalid specification")

                available_names = [q["name"] for q in specitem["queries"]]
                for k, v in definitions.items():
                    if (not isinstance(v, list)) or (len(v) == 0):
                        logger.error(
                            "Query specification items should have valid definition",
                            extra={
                                "transform": self.name,
                                "data": "Expected valid non-empty value. Found:\n{}".format(
                                    definition
                                ),
                            },
                        )
                        raise Exception("Invalid specification")
                    missing = [name for name in v if name not in available_names]
                    if len(missing) > 0:
                        logger.error(
                            "Query specification items should have valid definition",
                            extra={
                                "transform": self.name,
                                "data": "Missing: {}\n{}".format(missing, definition),
                            },
                        )
                        raise Exception("Invalid specification")

        # Last check whether the requirements can be satisfied
        names = self.args["names"]

        available_names = ["all"]
        for specitem in spec:
            if "definitions" in specitem:
                available_names.extend(list(specitem["definitions"].keys()))
            for q in specitem["queries"]:
                available_names.append(q["name"])

        missing = [name for name in names if name not in available_names]
        if len(missing) > 0:
            logger.error(
                "Invalid names in args",
                extra={
                    "transform": self.name,
                    "data": "Missing: {}\nAvailable: {}".format(
                        missing, available_names
                    ),
                },
            )
            raise Exception("Invalid specification")

    #############################################################
    # Output
    #############################################################
    def get_output_handler(self, query, params):
        """
        Find a handler for the output of the query. This function
        should be over-ridden to compute the handler dynamically.

        """
        if "output" not in query:
            raise Exception("Unable to determine output handler. No 'output' in query")

        if isinstance(query["output"], str):
            return FileOutputHandler(self, query["output"])

            raise Exception("Unable to determine output. No 'output' in query")

    #############################################################
    # Executors..
    #############################################################
    def get_executor(self, specitem, query, credentials):
        """
        Get executor for a specitem and credentials. This executor
        runs the query.

        The executor could be specified within the query,
        spec, or could default to built-in one based on the
        credentials and dbtype within.

        Args:

            spec (dict): Specification of the query
            query (dict): Particular query to execute
            credentials (dict): Credentials for the backend

        Returns:

            a callable executor
        """

        default_executor = None
        if credentials["dbtype"] == "mysql":
            default_executor = self.mysql_executor
        elif credentials["dbtype"] == "hive":
            default_executor = self.hive_executor

        # Executor can be per query or for the entire set
        executor = query.get("executor", specitem.get("executor", default_executor))

        if (executor is not None) and callable(executor):
            return executor

        if (executor is not None) and hasattr(self, executor):
            return getattr(self, executor)

        raise Exception("Cant find executor: {}".format(executor))

    def mysql_executor(self, specitem, credentials, query, params):
        """
        Built in executor for queries against a mysql backend. The output
        is dumped to a temporary file and then an output handler is called
        for post-processing.

        Args:

            spec (dict): Specification of the query
            query (dict): Particular query to execute
            credentials (dict): Credentials for the backend

        """
        try:

            targetdir = None

            # Should this be forced?
            force = self.args.get("force", False)
            cleanup = self.args.get("cleanup", True)

            # Get the output filename (s3, hdfspath etc.)
            handler = self.get_output_handler(query, params)

            if (not force) and handler.exists(params):
                logger.debug(
                    "[Skipping:Exists] {} {}".format(query["name"], params["dt"]),
                    extra={"transform": self.name},
                )
                return

            logger.debug(
                "[Computing] {} {}".format(query["name"], params["dt"]),
                extra={"transform": self.name},
            )

            # Create a temp directory
            targetdir = tempfile.mkdtemp(prefix="query_executor_")

            # Process the credentials
            config = get_mysql_config(credentials)

            # Create the environment file
            cnfname = os.path.join(targetdir, "env.sh")
            with open(cnfname, "w") as fd:
                fd.write("[client]\n")
                for var in ["host", "user", "password"]:
                    fd.write("{}={}\n".format(var, config[var]))

            # Instantiate the sql
            sqlfile = self.get_file(query["sql"])
            if not os.path.exists(sqlfile):
                raise Exception("Invalid sql file: {}".format(sqlfile))
            sql = open(sqlfile).read()

            # Resolve the sql content
            sql = sql.format(**params)

            sqlname = os.path.join(targetdir, "run.sql")
            with open(sqlname, "w") as fd:
                fd.write(sql)

            # => Now write the script
            tmpname = os.path.join(targetdir, "output.tsv")

            cmd = "mysql --defaults-extra-file={}".format(cnfname)

            # Generate the script to run
            script = """#!/bin/bash\n\n"""
            script += "date\n"
            script += "{} -B < {} > {}\n".format(cmd, sqlname, tmpname)
            script += "date\n"
            script += "[ -s {0} ] && sed -i 's/\\r//g' {0}\n".format(tmpname)
            scriptname = os.path.join(targetdir, "run.sh")
            with open(scriptname, "w") as fd:
                fd.write(script)

            try:
                process = subprocess.Popen(
                    ["/bin/bash", scriptname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                out, err = process.communicate()
                logger.debug(
                    "Executed the script",
                    extra={
                        "transform": self.name,
                        "data": "Output:\n----\n"
                        + out.decode("utf-8")
                        + "\n\nError:\n-----\n"
                        + err.decode("utf-8"),
                    },
                )
            except:
                logger.exception(
                    "Error while executing the script",
                    extra={
                        "transform": self.name,
                    },
                )

            # => Now post-process it..
            handler.process(tmpname, params)

        except:
            logger.exception("Failed to execute", extra={"transform": self.name})

        try:
            if cleanup and (targetdir is not None) and os.path.exists(targetdir):
                shutil.rmtree(targetdir)
            else:
                logger.warning(
                    "Targetdir not removed",
                    extra=self.config.get_extra(
                        {
                            "transform": self.name,
                            "data": "Targetdir: {}".format(targetdir),
                        }
                    ),
                )
        except:
            logger.exception(
                "Cleanup failed",
                extra=self.config.get_extra(
                    {"transform": self.name, "data": "Targetdir: {}".format(targetdir)}
                ),
            )

    def hive_executor(self, specitem, credentials, query, params):
        """
        Built in executor for queries against a hive backend. The output
        is dumped to a temporary file and then an output handler is called
        for post-processing.

        Args:

            spec (dict): Specification of the query
            query (dict): Particular query to execute
            credentials (dict): Credentials for the backend

        """
        try:

            targetdir = None

            # Should this be forced?
            force = self.args.get("force", False)
            cleanup = self.args.get("cleanup", True)

            # Get the output filename (s3, hdfspath etc.)
            handler = self.get_output_handler(query, params)

            if (not force) and handler.exists(params):
                logger.debug(
                    "[Skipping:Exists] {} {}".format(query["name"], params["dt"]),
                    extra={"transform": self.name},
                )
                return

            logger.debug(
                "[Computing] {} {}".format(query["name"], params["dt"]),
                extra={"transform": self.name},
            )

            # Create a temp directory
            targetdir = tempfile.mkdtemp(prefix="query_executor_")

            # Process the credentials
            config = get_mysql_config(credentials)

            # Instantiate the sql
            sqlfile = self.get_file(query["sql"])
            if not os.path.exists(sqlfile):
                raise Exception("Invalid sql file: {}".format(sqlfile))
            sql = open(sqlfile).read()

            # Resolve the sql content
            sql = sql.format(**params)

            sqlname = os.path.join(targetdir, "run.sql")
            with open(sqlname, "w") as fd:
                fd.write(sql)

            # => Now write the script
            tmpname = os.path.join(targetdir, "output.tsv")

            cmd = (
                "beeline -u jdbc:hive2://%(host)s:%(port)s --silent=true --verbose=False --outputformat=tsv"
                % config
            )

            if "user" in config:
                cmd += " -n '{}'".format(user)

            if "password" in config:
                cmd += " -p '{}'".format(password)

            # Generate the script to run
            script = """#!/bin/bash\n\n"""
            script += "date\n"
            script += "{} -f {} > {}\n".format(cmd, sqlname, tmpname)
            script += "date\n"
            script += "[ -s {0} ] && sed -i 's/\\r//g' {0}\n".format(tmpname)
            scriptname = os.path.join(targetdir, "run.sh")
            with open(scriptname, "w") as fd:
                fd.write(script)

            try:
                process = subprocess.Popen(
                    ["/bin/bash", scriptname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                out, err = process.communicate()
                logger.debug(
                    "Executed the script",
                    extra={
                        "transform": self.name,
                        "data": "Output:\n----\n"
                        + out.decode("utf-8")
                        + "\n\nError:\n-----\n"
                        + err.decode("utf-8"),
                    },
                )
            except:
                logger.exception(
                    "Error while executing the script",
                    extra={
                        "transform": self.name,
                    },
                )

            # => Now post-process it..
            handler.process(tmpname, params)

        except:
            logger.exception("Failed to execute", extra={"transform": self.name})

        try:
            if cleanup and (targetdir is not None) and os.path.exists(targetdir):
                shutil.rmtree(targetdir)
            else:
                logger.warning(
                    "Targetdir not removed",
                    extra=self.config.get_extra(
                        {
                            "transform": self.name,
                            "data": "Targetdir: {}".format(targetdir),
                        }
                    ),
                )
        except:
            logger.exception(
                "Cleanup failed",
                extra=self.config.get_extra(
                    {"transform": self.name, "data": "Targetdir: {}".format(targetdir)}
                ),
            )

    #########################################################
    # Generators of parameters
    #########################################################
    def get_generator(self, specitem, query):
        """
        Parameters generator. This is useful when a templatized
        query has to be run against the backend over many
        days. The output of the generator function is a list of
        dictionaries each of which is a key-value set for one
        time window (say a day)

        Args:

            spec (dict): Specification of the query
            query (dict): Particular query to execute

        Returns:

            a callable generator function
        """
        generator = query.get("generator", specitem.get("generator", "generator_daily"))
        if (generator is not None) and callable(generator):
            return generator

        if (generator is not None) and hasattr(self, generator):
            return getattr(self, generator)

        raise Exception("Could not find generator: {}".format(generator))

    def generator_daily(self, spec, specitem, query):
        """
        Built-in function to generate a list of dates (one for each day)
        between two dates.

        """

        start = self.args["start"]
        end = self.args["end"]
        if start > end:
            start, end = end, start

        if isinstance(start, datetime):
            start = start.date()
        if isinstance(end, datetime):
            end = end.date()

        # Pass any extra parameters
        extra = query.get("params", {})
        paramlist = []
        dt = start
        while dt < end:
            params = {"dt": dt.isoformat()}
            params.update(extra)

            dt += relativedelta.relativedelta(days=1)
            paramlist.append(params)

        return paramlist

    def process_specitem(self, spec, specitem, toexecute):

        logger.debug(
            "Executing {}".format(specitem["name"]),
            extra={
                "transform": self.name,
                "data": "To Execute: " + ", ".join(toexecute),
            },
        )

        # What should we be talking to?
        cred = self.get_credentials(specitem["cred"])

        nature = cred.get("nature", "unknown")
        dbtype = cred.get("dbtype", "unknown")

        # => Sanity check the credentials
        if (nature not in ["db"]) or (dbtype not in ["mysql", "hive"]):
            logger.error(
                "Invalid credentials",
                extra={
                    "transform": self.name,
                    "data": "Nature should be 'db' and dbtype should be 'mysql'",
                },
            )
            raise Exception("Invalid credentials")

        for query in specitem["queries"]:
            if query["name"] in toexecute:
                # Get how to executor the query...
                executor = self.get_executor(specitem, query, cred)
                generator = self.get_generator(specitem, query)
                paramlist = generator(spec, specitem, query)
                for params in paramlist:
                    try:
                        executor(
                            specitem=specitem,
                            credentials=cred,
                            query=query,
                            params=params,
                        )
                    except:
                        logger.exception(
                            "Failed to execute: {} {}".format(
                                query["name"], params["dt"]
                            ),
                            extra={"transform": self.name},
                        )

    def process_spec(self, spec):
        """
        Process query specification
        """

        names = self.args["names"]
        for specitem in spec:

            try:

                itemname = specitem["name"]

                enable = specitem.get("enable", True)
                if not enable:
                    logger.error(
                        "Skipping: {}. Not enabled.".format(itemname),
                        extra={"transform": self.name},
                    )
                    continue

                # What should we be executing to begin with..?
                toexecute = []
                for name in names:
                    if name in specitem.get("definitions", {}):
                        toexecute.extend(specitem["definitions"][name])

                for q in specitem["queries"]:
                    if (name == "all") or (q["name"] == name):
                        toexecute.append(q["name"])

                # Cleanup
                toexecute = list(set(toexecute))

                if len(toexecute) == 0:
                    logger.error(
                        "No parameter list generated: {}".format(itemname),
                        extra={"transform": self.name},
                    )
                    continue

                # Now process the list of queries. Params will be
                # generated per specitem.
                self.process_specitem(spec, specitem, toexecute)

                logger.debug(
                    "Completed execution: {}".format(itemname),
                    extra={"transform": self.name},
                )
            except:
                logger.exception(
                    "Unable to execute: {}".format(itemname),
                    extra={"transform": self.name},
                )

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Starting Query Execution",
            extra=self.config.get_extra({"transform": self.name}),
        )

        start = self.args["start"]
        end = self.args["end"]

        # Get and validate spec
        spec = self.get_spec()
        self.validate_spec(spec)
        try:
            self.process_spec(spec)
        except:
            logger.exception(
                "Failed while processing spec", extra={"transform": self.name}
            )
            raise

        logger.debug(
            "Completed Query Execution",
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
