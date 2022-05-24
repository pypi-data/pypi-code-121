import os
import sys
import json
import re
from datetime import datetime
import traceback
import pandas as pd
from s3fs import S3FileSystem
from ..lib.exceptions import NoDataFound

from dateutil import parser as dateparser
from datetime import datetime, date, timedelta


class DataSource(object):
    """
    Class for specifying a dataset. This is a base class
    meant to be derived and implemented.
    """

    def __init__(self, params, *args, **kwargs):

        self._type = params.get("type", "unknown")
        """
        Type of the dataset.
        """

        self.name = params["name"]
        """
        Unique name of the dataset, e.g., Events
        """

        self.description = params.get("description", "")
        """
        str: Description
        Example: "Daily events for Alpha Sensor"
        """

        alt_names = params.get("alt_names", [])
        if not isinstance(alt_names, list):
            alt_names = [alt_names]
        alt_names = [str(x) for x in alt_names]
        self.alt_names = alt_names
        """
        list: Alternative names for the dataset
        Example: "['txn_charges']"
        """

        self.version = params.get("version", "v1")
        """
        str: Version
        Example: "v1"
        """

        self.resolve = kwargs.get("resolve", params.get("resolve", {}))
        """
        Parameters to resolve paths
        """

        # Backward compatability
        if "paths" not in params:
            params["paths"] = []
            for name in ["local", "test", "backup"]:
                if name in params:
                    params["paths"].append(
                        {
                            "name": name,
                            "nature": "s3" if name == "backup" else "local",
                            "path": params[name],
                        }
                    )

        self.validate(params)

        self._type = "File"

        self.isfile = params.get("isfile", False)
        """
        Specifies whether the dataset is simple (a file for each
        run) or more complex directory hierarchy.

        Example::

            # A complex dataset
            Dataset(params={
                "name": 'athena-availability',
                "isfile": False,
                ...

        """
        self.issortable = params.get("issortable", True)

        self.subsets = params.get("subsets", [])
        """
        A dataset oftentimes has multiple components. Define
        them here. We can give a name to each.

        Example::

          {
             ...
             "subsets": [
                 {
                     "name": "v1culltable",
                     "pattern": ".*v1culltable.csv$"
                 },...
              ]
          }
        """

        self.paths = params.get("paths", {})
        """
        dict: Paths to be resolved
        Example::

            [
              {
                "name": "test",
                "nature": "local",
                "path": "%(data_root)s/shared/datasets/athena/v2/availability"
              }
           ]
         """

        self.registry = None
        """
        object: Dataset manager object
        """

    def matches(self, names):
        """
        Check if the dataset has a particular name
        """
        if not isinstance(names, list):
            names = [names]

        matches = [((name == self.name) or (name in self.alt_names)) \
                                   for name in names]
        return any(matches)

    def set_resolve(self, resolve):
        """
        Allow the user to specify a resolving dict
        """
        assert isinstance(resolve, dict)
        assert len(resolve) > 0
        self.resolve.update(resolve)

    def set_registry(self, registry):
        """
        Set the registry object
        """
        self.registry = registry

    def get_paths(self):
        """
        Return the available paths (full list of dictionaries,
        not just the names
        """
        return self.paths

    def get_path_by_name(self, name, full=False, resolve=None):
        """
        Return the path definition for a path with a given name
        """

        if resolve is None:
            resolve = self.resolve

        selected = None
        for p in self.paths:
            if p["name"] == name:
                selected = p
                break
        if selected is None:
            raise Exception("Path with name {} not present".format(name))

        if full:
            return selected

        path = selected["path"]

        try:
            if (
                (resolve is not None)
                and (isinstance(resolve, dict))
                and (len(resolve) > 0)
            ):
                path = path % resolve
        except:
            raise Exception("Path could not be resolved")

        return path

    def get_path_by_nature(self, nature, full=True, resolve=None):

        if resolve is None:
            resolve = self.resolve

        selected = None
        for p in self.paths:
            if p["nature"] == nature:
                selected = p
                break

        if selected is None:
            raise Exception("Path with nature {} not present".format(nature))

        if full:
            return selected

        path = selected["path"]

        try:
            if (
                (resolve is not None)
                and (isinstance(resolve, dict))
                and (len(resolve) > 0)
            ):
                path = path % resolve
        except:
            raise Exception("Path could not be resolved")

        return path

    def has_subsets(self):
        """
        Does this dataset have components?
        """
        return len(self.subsets) > 0

    def get_subsets(self):
        """
        Return the names of subsets available
        """
        return [s["name"] for s in self.subsets]

    def get_subset_description(self, name):
        """
        Get the description for a subset
        """
        for s in self.subsets:
            if s["name"] == name:
                return s.get("description", self.description)

        raise Exception("Unknown subset: {}".format(name))

    def in_subset(self, name, spec):
        """
        Return the names of subsets available
        """

        if (not isinstance(spec, dict)) or (len(spec) == 0) or ("filename" not in spec):
            raise Exception("invalid subset check input. Expecting dict with filename")

        # Does the subset name exist?
        subset = None
        for s in self.subsets:
            if name == s["name"]:
                subset = s
                break
        if subset is None:
            return False

        #
        if "pattern" not in subset:
            return False

        filename = spec["filename"]
        pattern = subset["pattern"]
        return re.search(pattern, filename) is not None

    def get_path(self, name, full=False, resolve=None):
        return self.get_path_by_name(name, full, resolve)

    def validate(self, params):
        """ """
        if not isinstance(params, dict):
            raise Exception("Invalid parameters for dataset")

        for col in ["name", "paths"]:
            if col not in params:
                raise Exception("Data specification should have {}".format(col))

        if not isinstance(params["paths"], list):
            raise Exception("Paths should be a list of dictionaries")

        for elem in params["paths"]:
            if not isinstance(elem, dict) or len(elem) == 0:
                raise Exception("paths element should be non-empty dict")
            if ("nature" not in elem) or (elem["nature"] not in self.valid_natures):
                raise Exception(
                    f"paths element have nature {'|'.join(self.valid_natures)}"
                )
            if "path" not in elem:
                raise Exception("paths element should have a 'path'")

    def __str__(self):
        return "[{}] {}".format(self._type, self.name)


class Dataset(DataSource):
    """
    Class for specifying a dataset. This is typically
    an input to the transforms.

    Usage::

        # A dataset that has one directory for each day. Within that
        # there are atleast two sub-datasets
        Dataset(params={
            "name": 'athena-availability',
            "type": "file",
            "paths": [
                {
                    "name": "test",
                    "nature": "local",
                    "path": "%(data_root)s/shared/datasets/athena/v2/availability",

                },
                {
                    "name": "local",
                    "nature": "local",
                    "path": "%(enrich_data_dir)s/acme/Marketing/shared/datasets/athena/v2/availability",
                },
                {
                    "name": "s3",
                    "nature": "s3",
                    "path": "%(backup_root)s/%(node)s/data/acme/Marketing/shared/datasets/athena/v2/availability",
                },
            ],
            "match": {
                "generate": "generate_datetime_daily",
                "compare": "compare_datetime_pattern_match_range",
                "pattern": "%Y-%m-%d",
            },
            "subsets": [
                {
                    "name": "CatalogScore",
                    "pattern": ".*catalogscore.csv$",
                    "description": "Score of all products in the catalog"
                },
                {
                    "name": "ProductWeight",
                    "pattern": ".*productweight.csv$",
                    "description": "Assortment weight for each product"
                }
            ]
        })

    """

    def __init__(self, params, *args, **kwargs):

        super().__init__(params, *args, **kwargs)

        self.match = params.get("match", {})
        """
        dict: Generating and matching rules

        Example::

            {
                "generate": "generate_datetime_daily",
                "match": "match_datetime_pattern_range",
                "pattern": "plpevents-%Y%m%d-%H%M%S",
            }
        """

    def sample(self, filename, safe=True, fd=None, nrows=10):
        """
        Sample a file belonging to this dataset.Subclass and
        overload this function if the data is sensitive.

        Args:
            filename (str): A file that belongs to this dataset
            safe (bool): Whether file is trusted
            fd (object): File descriptor for s3/gcs/other non-filesystems
            nrows (int): Number of rows to sample
        """

        if fd is None:
            # Text formats..
            if filename.split(".")[-1].lower() in ["csv", "tsv"]:
                fd = open(filename)
            else:
                fd = open(filename, "rb")

        # Read the file
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(fd, nrows=nrows)
        elif filename.lower().endswith(".csv.gz"):
            df = pd.read_csv(fd, nrows=nrows, compression="gzip", error_bad_lines=False)
        elif filename.lower().endswith(".tsv.gz"):
            df = pd.read_csv(
                fd, nrows=nrows, sep="\t", compression="gzip", error_bad_lines=False
            )
        elif filename.lower().endswith(".tsv"):
            df = pd.read_csv(fd, nrows=nrows, sep="\t")
        elif filename.lower().endswith(".pq") or filename.lower().endswith(
            ".pq.sample"
        ):
            df = pd.read_parquet(fd)
            if nrows is not None:
                df = df.head(nrows)
        else:
            raise Exception(f"Unknown file format: {filename}")

        return df

    @property
    def local(self):
        """
        Read the path with the name 'local'. Available for
        backward compatability
        """
        return self.get_path("local")

    @property
    def test(self):
        """
        Read the path with the name 'test'. Available for
        backward compatability
        """
        return self.get_path("test")

    @property
    def backup(self):
        """
        Read the path with the name 'backup'. Available for
        backward compatability
        """
        return self.get_path("backup")

    @property
    def valid_natures(self):
        return ["local", "remote", "s3", "gcs"]

    def validate(self, params):
        """
        Validate dataset arguments. It should be a dictionary
        with atleast three elements: name, match, and paths.

        Args:
          params (dict): Parameters for dataset

        Params dict should have the following:

          * name: string
          * match: dictionary with generate function (name or lambda), are function (name or lambda), and pattern (string).

        """

        super().validate(params)

        # If match is specified, then do something...
        if ("match" not in params) or (not isinstance(params["match"], dict)):
            raise Exception("Match should be a valid dictionary")

        if "pattern" not in params["match"]:
            raise Exception("Matching requirement match.pattern missing")

        pattern = params["match"]["pattern"]
        if not isinstance(pattern, str) and not callable(pattern):
            raise Exception("Invalid pattern specification")

        generate = params["match"].get("generate", "generate_datetime_daily")

        if ((isinstance(generate, str)) and (not hasattr(self, generate))) and (
            not callable(generate)
        ):
            raise Exception("Matching requirement {} missing/invalid".format(generate))

        compare = params["match"].get("compare", "compare_datetime_pattern_match_range")
        if ((isinstance(compare, str)) and (not hasattr(self, compare))) and (
            not callable(compare)
        ):
            raise Exception("Matching requirement {} missing/invalid".format(compare))

    def generate(self, start, end=None, full=False, name="default", resolve=None):
        """
        Given a start and an end, generate the datetime
        objects corresponding to each run

        Args:
           start (datetime): Start of the time range
           end (datetime): End of range. If None, default = start
           full (bool): Whether full path is required or only the suffix. Default is false
           name (str): Name of the path specification. Optional is full path is required
           resolve (dict): Additional path resolution parameters

        Returns:
           list (dict): List of dictionaries (name, timestamp)

        """
        if (not isinstance(start, (datetime, date))) or (
            (end is not None) and (not isinstance(end, (datetime, date)))
        ):
            raise Exception("Start or end is not a datetime/date")

        # One day
        if end is None:
            end = start

        # Handle ordering...
        if end < start:
            start, end = end, start

        func = self.match["generate"]
        if isinstance(func, str):
            func = getattr(self, func)

        # Generate all possible names
        names = func(start, end)

        # Now insert the full path...
        try:
            if full:
                path_root = self.get_path_by_name(name, resolve=resolve)
                for n in names:
                    n['path'] = os.path.join(path_root, n['name'])
        except:
            logger.exception("Unable to resolve names")

        # Check if the name is in the names..
        return names

    def generate_datetime_daily(self, start, end):
        """
        Given a start and an end, generate the datetime
        objects corresponding to each run for each day.

        Args:
           start (datetime): Start of the time range
           end (datetime): End of range. If None, default = start
        """

        pattern = self.match["pattern"]

        names = []
        current = start
        while current <= end:
            if isinstance(pattern, str):
                name = current.strftime(pattern)
            elif callable(pattern):
                name = pattern(current)
            else:
                raise Exception("Unsupported pattern type")

            names.append({"timestamp": current.isoformat(), "name": name})
            current += timedelta(days=1)

        return names

    def compare_datetime_pattern_match_range(self, name, start, end):
        """
        Given a start and an end, generate the datetime
        objects corresponding to each run for each day, and
        check whether a named file/directory exists in that list.

        Args:
           start (datetime): Start of the time range
           end (datetime): End of range. If None, default = start
        """

        if not isinstance(name, str):
            return False

        # Generate all possible <timestamp>: <name> combinations
        names = self.generate(start, end)

        # names is a dict {'timestamp': '2021-02-02T13:24:11', 'name': '2021-02-02'}
        names = [n["name"] for n in names]
        # Check if the name is in the names or in the range. The
        # latter is required if there are multiple runs in a given day
        #
        return (name in names) or ((name >= min(names) and name <= max(names)))

    def match_content(self, fs, localdir, backupdir, dirname):
        """
        Check whether local path is replicated in the  s3/blob store

        Args:
           fs (object): s3fs handle
           localdir (str): Root local dir to check
           backupdir (str): Root remote dir in block store to check
           dirname (str): path within the localdir
        """

        localpath = os.path.join(localdir, dirname)
        if os.path.isfile(localpath):
            filesize = getsize(localpath)
            backupfile = os.path.join(backupdir, dirname)
            try:
                detail = fs.info(backupfile)
            except FileNotFoundError:
                return False, "Missing file in backup ({})".format(dirname)
            except Exception as e:
                return False, str(e)

            if filesize != detail["size"]:
                return False, "Filesize mismatch: {}".format(dirname)

            return True, "Matched {} (size: {}M)".format(
                dirname, round(filesize / 1000000, 1)
            )

        matched = 0
        totalsize = 0
        for root, dirs, files in os.walk(localpath):
            for name in files:
                filename = os.path.join(root, name)
                relpath = os.path.relpath(filename, start=localpath)
                backupfile = os.path.join(backupdir, dirname, relpath)
                filesize = getsize(filename)
                try:
                    detail = self.fs.info(backupfile)
                except FileNotFoundError:
                    return False, "Missing file in backup ({})".format(relpath)
                except Exception as e:
                    return False, str(e)

                if filesize != detail["size"]:
                    return False, "Filesize mismatch: {}".format(relpath)

                matched += 1
                totalsize += filesize

        return True, "Matched {} (size: {}M)".format(
            matched, round(totalsize / 1000000, 1)
        )

    def compare(self, name, start, end=None):
        """
        Given a start and an end, generate the datetime
        objects corresponding to each run

        Args:
           name (str): Directory name
           start (datetime): Start of the time range
           end (datetime): End of range. If None, default = start

        """
        if (not isinstance(start, datetime)) or (
            (end is not None) and (not isinstance(end, datetime))
        ):
            raise Exception("Generate names in the range")

        # One day
        if end is None:
            end = start

        # Handle ordering...
        if end < start:
            start, end = end, start

        func = params["match"].get("compare", "compare_datetime_pattern_match_range")
        if isinstance(func, str):
            func = getattr(self, func)

        # Generate all possible names
        return func(name, start, end)

    def listdir(self, name, fshandle=None, resolve=None, detail=False):
        """
        List the dataset directory
        """

        selected = None
        for p in self.paths:
            if p["name"] == name:
                selected = p
                break

        if selected is None:
            raise Exception("Unknown name of path: {}".format(name))

        if (selected["nature"] in ["s3", "gcs"]) and (
            (fshandle is None) or (not isinstance(fshandle, S3FileSystem))
        ):
            raise Exception(
                "Filesystem handle should be provided when nature is s3|gcs"
            )

        if not isinstance(detail, bool):
            raise Exception("detail is a boolean field")

        path = self.paths[name]

        try:
            if (
                (resolve is not None)
                and (isinstance(resolve, dict))
                and (len(resolve) > 0)
            ):
                path = path % resolve
        except:
            raise Exception("Path could not be resolved")

        if fshandle is None:
            return os.listdir(path)

        results = fshandle.listdir(path, detail=detail)
        if not detail:
            results = [os.path.basename(r) for r in results]

        return results

    def read_data(
        self,
        start_date,
        end_date,
        filename,
        readfunc,
        errors=True,
        name="default",
        params={},
        resolve={},
    ):
        """
        Read a single dataset

        Args:
             start_date (str): Starting date to scan
             end_date (str): Ending date of the scane
             filename (str): Filename within each day's directory
             readfunc (method): Callback
             errors (bool): What to do on failure. True = bailout
             name (str): Which subset to look at?
             params (dict): Params to the readfunc
             resolve (dict): Parameters for resolution of path

        Returns:
             dataframe: Data read
             dict: Optional metadata on the read

        """

        dates = self.generate(start_date, end_date)
        if len(dates) == 0:
            raise Exception("No dates found")

        # Get the path template...
        path = self.get_path_by_name(name, resolve)

        metadata = {"start": datetime.now(), "files": []}
        # Now compose all the dataframes...
        _dfs = []
        for dt in dates:
            fullpath = os.path.join(path, dt["name"], filename)
            try:
                metadata["files"].append(fullpath)
                df = readfunc(fullpath, params, date=dt["name"])
                if (df is None) or (len(df) == 0):
                    continue
            except:
                if errors:
                    raise
            _dfs.append(df)

        if len(_dfs) == 0:
            raise NoDataFound()

        df = pd.concat(_dfs, ignore_index=True)
        del _dfs

        metadata["end"] = datetime.now()

        # Note the access metadata
        if ((self.registry is not None) and
            (hasattr(self.registry, "access")) and
            (callable(self.registry.access))):
            self.registry.access(self, metadata, nature="read")

        return df, metadata

    def write_data_note(
        self,
            metadata
    ):
        # Note the access metadata
        if ((self.registry is not None) and
            (hasattr(self.registry, "access")) and
            (callable(self.registry.access))):
            self.registry.access(self, metadata, nature="read")


class DatabaseTable(DataSource):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params, *args, **kwargs)
        self._type = "DBTable"

    @property
    def valid_natures(self):
        return ["db"]


class Arg:
    """
    Dataset command argument
    """

    def __init__(self, name, description, *args, **kwargs):
        self.name = name
        self.description = description

    def find(self, datasource):
        """
        Find value values
        """
        raise Exception("Not implemented")

    def validate(self, datasource, value):
        raise Exception("Not implemented")

    def resolve(self, datasource, value, resolve=None):
        raise Exception("Not implemented")


class DateArg(Arg):
    """
    Datetime
    """

    def __init__(self, name, *args, **kwargs):
        super().__init__(name, "Date within past 1 year", *args, **kwargs)

    def find(self, datasource):
        today = datetime.now().date()
        return today

    def validate(self, datasource, value):
        today = datetime.now()
        try:
            dt = dateparser.parse(value)
            diff = today - dt
            if (diff.days > 365) or (diff.days < 0):
                return False
            return True
        except:
            return False

    def resolve(self, datasource, value, resolve):
        dt = dateparser.parse(value)
        return dt


class DatasetPathNatureArg(Arg):
    def __init__(self, name, nature, *args, **kwargs):

        super().__init__(name, "Path of type: {}".format(nature), *args, **kwargs)
        self.nature = nature

    def find(self, datasource):

        valid = []
        for p in datasource.paths:
            if p["nature"] == self.nature:
                valid.append(p["name"])

        return valid

    def validate(self, datasource, value):

        if not isinstance(datasource, Dataset):
            return False

        for p in datasource.paths:
            if (p["name"] == value) and (p["nature"] == self.nature):
                return True

        return False

    def resolve(self, datasource, value, resolve=None):

        if not isinstance(datasource, Dataset):
            raise Exception("Invalid datasource. Expected dataset")

        return datasource.get_path_by_name(value, resolve=resolve)


def get_commands():

    src_s3 = DatasetPathNatureArg("src", "s3")
    dst_s3 = DatasetPathNatureArg("dst", "s3")
    src_local = DatasetPathNatureArg("src", "local")
    dst_local = DatasetPathNatureArg("dst", "local")
    start = DateArg("start")
    end = DateArg("end")

    commands = [
        {
            "source_type": ["File"],
            "args": [src_s3, dst_local, start, end],
            "name": "s3-to-local",
            "description": "Download to local data directory",
            "command": "aws s3 sync s3://%(source)s/%(subdir)s%(slash)s %(destination)s/%(subdir)s%(slash)s",
        },
        {
            "source_type": ["File"],
            "args": [src_local, dst_s3, start, end],
            "name": "local-to-s3",
            "description": "Upload from local data directory to s3",
            "command": "aws s3 sync %(source)s/%(subdir)s%(slash)s s3://%(destination)s/%(subdir)s%(slash)s",
        },
        {
            "source_type": ["File"],
            "args": [src_s3, dst_s3, start, end],
            "name": "s3-to-s3",
            "description": "Sync from one s3 path to another s3 path",
            "command": "aws s3 sync s3://%(source)s/%(subdir)s%(slash)s s3://%(destination)s/%(subdir)s%(slash)s",
        },
        {
            "source_type": ["File"],
            "args": [src_local, dst_local, start, end],
            "name": "remote-to-local",
            "description": "Copy from remote local to test",
            "command": "scp -C -r ubuntu@%(node)s:%(source)s %(destination)s/%(subdir)s",
        },
        {
            "source_type": ["File"],
            "args": [src_local, dst_local, start, end],
            "name": "local-to-remote",
            "description": "Copy from test to remote local path",
            "command": "scp -C -r %(destination)s/%(subdir)s ubuntu@%(node)s:%(source)s",
        },
    ]

    return commands


class DatasetRegistry(object):
    """
    Registry for datasets.

    This provides a search and resolution interface.

    There is a notion of a command - a scp/aws command line template.
    The registry allows enumeration of the commands and enables
    scripting.

    """

    def __init__(self, *args, **kwargs):
        """

        Args:
            commands (list): List of command templates. Optional. If not specified,
                             the system will use defaults.
            resolve (dict): Path resolution dictionary

        """
        self.commands = kwargs.get("commands", get_commands())
        self.resolve = kwargs.get("resolve", {})
        self.state = kwargs.get('state', None)
        self.transform = kwargs.get('transform', None)
        if ((self.state is None) and (hasattr(self.transform, 'state'))):
            self.state = getattr(self.transform, 'state')

        self.datasets = []
        self.validate()

    def validate(self):
        for c in self.commands:
            assert isinstance(c, dict)
            assert ("source_type" in c) and (isinstance(c["source_type"], list))
            assert "args" in c
            assert isinstance(c["args"], list)
            assert "name" in c
            assert "command" in c
            assert isinstance(c["command"], str)
            assert len(c["command"]) > 0

    def get_command(self, name, source_type="File"):
        """
        Get the command specification by specifying its name

        Args:
            name (str): Name of the command template
        """
        for c in self.commands:
            if source_type not in c["source_type"]:
                continue
            if c["name"] == name:
                return c
        raise Exception("Missing command: {}".format(name))

    def get_commands(self, source_type="File"):
        """
        Get the command specifications as a list of dicts

        """
        if source_type is None:
            return self.commands

        # If specified, then apply that filter..
        return [c for c in self.commands if source_type in c["source_type"]]

    def add_datasets(self, items):
        """
        Add to the registry. Each element in the item list
        should be a Dataset (or subclass).

        Args:
           items (list): A list of datasets
        """
        if isinstance(items, list):
            for item in items:
                assert isinstance(item, DataSource)
                item.set_resolve(self.resolve)
                item.set_registry(self)
            self.datasets.extend(items)
        else:
            assert isinstance(items, DataSource)
            items.set_resolve(self.resolve)
            item.set_registry(self)
            self.datasets.append(items)

    def set_resolve(self, resolve):
        """
        Set the resolution parameters

        Args:
           resolve (dict): Resolution parameters

        """
        assert isinstance(resolve, dict)
        assert len(resolve) > 0
        self.resolve = resolve

    @property
    def params(self):
        return self.resolve

    def set_params(self, params):
        """
        Deprecated. Use set_resolve
        """
        return self.set_resolve(params)

    def list(self):
        """
        List all datasets in the registry
        """
        return [str(d) for d in self.datasets]

    def find(self, names):
        """
        Find a dataset in the registry.

        Args:
            names (str): Name of the dataset
        """
        if not isinstance(names, (list, str)):
            raise Exception(f"Unexpected dataset name(s): {names}")

        for d in self.datasets:
            if d.matches(names):
                return d

        return None

    def access(self, dataset, metadata, nature='read-write'):

        if self.state is None:
            # Nothing to be done
            return

        self.state.make_dataset_access_note(dataset, metadata, nature)
