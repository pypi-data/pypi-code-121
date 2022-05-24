import os
import sys
import json
import copy
import inspect
import glob
import pytz
import getpass
import platform
import traceback
import distro
from datetime import datetime
from dateutil import parser as date_parser

import pandas as pd

from ..core.frames import PandasDataFrame, DictDataFrame
from ..lib import read_siteconf, read_versionmap
from ..lib.context import Context
import logging


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if "DataFrame" in obj.__class__.__name__:
                return "<dataframe>"
            return super().default(obj)
        except:
            return str(obj)


logger = logging.getLogger("app")


class MockRun(object):
    def __init__(self, *args, **kwargs):
        self.state = kwargs.pop("state")
        self.files = []

    def load_files(self):
        frames = self.state.get_frame_list()
        for f in frames:
            detail = self.state.get_frame(f)
            detail["name"] = f
            self.files.append(detail)

    def list_files(self):
        return [f["name"] for f in self.files]

    def get_file_hash(self):
        return {f["name"]: f for f in self.files}


class MockRunManager(object):
    def __init__(self, *args, **kwargs):
        self.runs = []

    def load_runs(self, runs, state):
        for r in runs:
            status = r["status"]
            runid = r["runid"]
            run = MockRun(state=state)
            run.status = r["status"]
            run.runid = r["runid"]
            run.start_time = date_parser.parse(r["start_time"])
            run.end_time = date_parser.parse(r["end_time"])

            self.runs.append(run)

    def get_last_run(self, status="success"):
        for r in self.runs:
            if r.status == status:
                return r
        return run

    def load(self):
        pass


class MockState(object):
    def __init__(self, *args, **kwargs):
        self.name = "ExperimentalPipeline"
        self.runid = "exp-pipeline-20180922-192321"
        self.config = kwargs.pop("config", None)
        self.state = {}
        self.notes = []
        self.performance_notes = []
        self.expectations = []
        self.dataset_accesses = []
        self.notifications = {"email": []}
        user = getpass.getuser()
        self.pid = os.getpid()
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.stats = {
            "platform": {
                "node": platform.node(),
                "os": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "python": platform.python_version(),
                "distribution": distro.linux_distribution(),
            },
            "user": user,
        }

    def make_note(self, text):
        self.notes.append(text)

    def make_dataset_access_note(self, dataset, metadata, nature='read-write'):
        if dataset is None:
            return

        self.dataset_accesses.append({
            'timestamp': datetime.now(),
            'name': dataset.name,
            'nature': nature,
            'description': dataset.description,
            'metadata': metadata
        })

    def make_performance_note(
        self, name, description, condition, priority=1, message=""
    ):
        self.performance_notes.append(
            {
                "name": name,
                "description": description,
                "condition": condition,
                "priority": priority,
                "message": message,
            }
        )

    def update_frame(self, framename, details, create=False):

        details["name"] = framename

        for d in ["df", "transform"]:
            if d not in details:
                raise Exception("Missing frame detail: {}".format(d))
        if "frametype" not in details:
            details["frametype"] = "pandas"

        if "description" not in details:
            details["description"] = ""

        if "category" not in details:
            details["category"] = "default"

        if "stages" not in details:
            details["stages"] = []
        if isinstance(details["transform"], str):
            details["stages"].append(details["transform"])
        else:
            details["stages"].extend(details["transform"])

        if "params" not in details:
            details["params"] = []
        elif isinstance(details["params"], dict):
            details["params"] = [details["params"]]
        elif isinstance(details["params"], list):
            for p in details["params"]:
                if not isinstance(p, dict):
                    raise Exception("Invalid params. List items should be dicts")
        else:
            raise Exception("Invalid params. Expected list or dict")

        if "history" not in details:
            details["history"] = []
        elif isinstance(details["history"], dict):
            details["history"] = [details["history"]]

        if framename not in self.state:
            self.state[framename] = details
        else:
            frame = self.state[framename]
            frame["df"] = details["df"]
            frame["source"] = details["transform"]
            frame["stages"].append(details["transform"])
            frame["history"].extend(details["history"])

            # Handle description
            if (isinstance(details["description"], str)) and (
                len(details["description"]) > 0
            ):
                if frame["description"] != "":
                    frame["description"] += ". "
                frame["description"] += details["description"]

            # Incorporate params
            if "params" in details:
                if isinstance(details["params"], dict):
                    frame["params"].insert(0, details["params"])
                elif isinstance(details["params"], list):
                    for p in details["params"]:
                        if not isinstance(p, dict):
                            raise Exception("Invalid params type")
                        if len(p) == 0:
                            continue
                        frame["params"].append(p)
                else:
                    raise Exception("Unknown params")

            if (frame["category"] == "default") and (details["category"] != "default"):
                frame["category"] = details["category"]

    def has_frame(self, framename):
        return framename in self.state

    def get_frame(self, framename):
        if framename not in self.state:
            raise Exception("Cannot find the required frame")
        return self.state[framename]

    def get_frame_list(self, category=None):
        allframes = list(self.state.keys())
        if category is None:
            return allframes

        frames = []
        for f in allframes:
            if self.state[f]["category"] == category:
                frames.append(f)

        return frames

    def reached_stage(self, frame, name):
        return (frame in self.state) and (name in self.state[frame]["stages"])

    def add_expectations(self, transform, frame, expectations):
        if not isinstance(expectations, list):
            raise Exception("Expectations should be a list")

        for e in expectations:
            for col in ["expectation", "description", "passed"]:
                if col not in e:
                    raise Exception(
                        "Expectation results are missing col {}".format(col)
                    )

        # => Insert metadata and store
        expanded = []
        for e in expectations:
            e = copy.copy(e)
            e.update(
                {
                    "version": "v1",
                    "timestamp": self.config.now().isoformat(),
                    "frame": frame,
                    "meta": {
                        "node": self.stats["platform"]["node"],
                        "pipeline": self.name,
                        "transform": transform.name,
                        "runid": self.runid,
                        "start_time": self.start_time.isoformat(),
                    },
                }
            )
            self.expectations.append(e)


class MockConfig(object):
    def __init__(self, context={}, *args, **kwargs):

        # Initialize the context
        if len(context) == 0:
            context = Context()
            context.set_env()
            context = context.asdict()

        self.name = "TestConf"
        self.state = MockState(config=self)
        self.runid = "run-2015021"
        self.description = "Experimental pipeline for testing transforms"
        self.context = context
        self.runmanager = MockRunManager()
        self.dataframes = {"pandas": PandasDataFrame(), "dict": DictDataFrame()}
        self.tz = pytz.timezone("Asia/Kolkata")
        self.ts = datetime.now(self.tz).replace(microsecond=0).isoformat()
        self.enable_extra_args = True
        self.readonly = False
        self.data_root = self.context["ENRICH_TEST"]
        self.customer_root = self.context["ENRICH_CUSTOMERS"]
        self.enrich_customers = self.context["ENRICH_CUSTOMERS"]
        self.enrich_root = self.context["ENRICH_ROOT"]
        self.enrich_run_root = self.context["ENRICH_ROOT"]
        self.enrich_data_dir = self.data_root
        self.accessed_files = []
        self.supported_extra_args = []
        self.usecase = {"org": {"name": "Unknown", "customer": "unknown"}}
        # Add defaults
        for attr in [
            "data_root",
            "enrich_data_dir",
            "inputdir",
            "outputdir",
            "statedir",
        ]:
            setattr(self, attr, self.data_root)

    def get_usecase(self):
        return self.usecase.get("org", {}).get("name", "Unknown")

    def get_customer(self):
        return self.get_usecase()

    def load_usecase(self, path):

        enrichjson = None
        enrich_customers = self.enrich_customers

        if "ENRICHJSON" in os.environ:
            enrichjson = os.environ["ENRICHJSON"]
            enrichjson = os.path.abspath(enrichjson)
        elif "ENRICHJSON" in self.context:
            enrichjson = os.path.abspath(self.context["ENRICHJSON"])
        elif os.path.exists(enrich_customers):
            # Try inferring from the location.
            enrichjson = None
            path = os.path.realpath(path)
            for c in os.listdir(enrich_customers):
                c = os.path.realpath(os.path.join(enrich_customers, c))
                if path.startswith(c):
                    relpath = os.path.relpath(path, start=c)
                    enrichjson = os.path.join(
                        c, relpath.split(os.sep)[0], "enrich.json"
                    )
                    break

        if (enrichjson is None) or (not os.path.exists(enrichjson)):
            logger.warning("Unable to find enrich.json")
            return {}

        try:
            enrich = json.load(open(enrichjson))
        except:
            raise Exception("enrich.json should be valid json file")

        self.usecase = enrich

    def get_cmdline_args(self):
        return {}

    def configure(self, params):
        for var in ["enable_extra_args"]:
            if var in params:
                setattr(self, var, params[var])

    def now(self):
        return datetime.now(self.tz).replace(microsecond=0)

    def get_dataframe(self, name):

        if name == "pandas":
            return self.dataframes["pandas"]
        elif name == "dict":
            return self.dataframes["dict"]
        else:
            raise Exception("Unsupported dataframe type")

    def get_extra(self, extra={}):
        return extra

    def get_file(self, template, abspath=True, create_dir=False, extra={}):

        if template is None:
            return None

        now = self.now()
        dt = now.strftime("%Y-%m-%d")
        dtime = now.strftime("%Y%m%d-%H%M%S")
        node = platform.node()

        try:
            params = {
                "name": self.name,
                "outputdir": self.outputdir,
                "output": self.outputdir,
                "inputdir": self.inputdir,
                "input": self.inputdir,
                "statedir": self.statedir,
                "state": self.statedir,
                "runid": self.runid,
                "ts": self.ts,
                "date": dt,
                "datetime": dtime,
                "node": node,
                "data_root": self.data_root,
                "enrich_root": self.enrich_root,
                "enrich_data_dir": self.enrich_data_dir,
            }
            params.update(self.context)
            params.update(extra)
            filename = template % params
        except:
            error = "Invalid file specification: {}".format(template)
            raise Exception(error)

        if abspath:
            filename = os.path.abspath(filename)

        if create_dir:
            try:
                os.makedirs(os.path.dirname(filename))
            except:
                pass

        transform = extra.get("transform", None)
        meta = extra.get("meta", {})
        self.note_access(filename, transform, meta)

        return filename

    def note_access(self, filename, transform, meta={}):

        if transform is None:
            return

        code = None
        stack = inspect.stack()
        for s in stack:
            if (
                (".virtualenv" not in s.filename)
                and ("enrichcli" not in s.filename)
                and ("enrichsdk" not in s.filename)
            ):
                code = s.filename
                code = self.get_relative_path(code, what="enrich_root")
                code += ":" + str(s.lineno)
                break

        if os.path.abspath(filename):
            relpath = self.get_relative_path(filename, what="enrich_root")
        else:
            relpath = filename

        entry = {
            "transform": transform.name
            if not isinstance(transform, str)
            else transform,
            "filename": relpath,
            "timestamp": datetime.now().isoformat(),
            "source": code,
            "meta": meta,
        }

        self.accessed_files.append(entry)

    def get_relative_path(self, path, what="enrich_data_dir"):

        paths = {
            "enrich_root": self.enrich_root,
            "enrich_data_dir": self.enrich_data_dir,
            "outputdir": self.outputdir,
            "output": self.outputdir,
            "data_root": self.data_root,
        }
        whatroot = paths[what]
        return os.path.relpath(path, whatroot)

    def load_test_state(self, testdata):

        app = {
            "pipeline": self.name,
            "description": self.description,
            "data_root": self.data_root,
            "customer_root": self.customer_root,
            "runid": self.runid,
        }

        # Load siteconf
        if "siteconf" in testdata:
            siteconf = read_siteconf(
                testdata["siteconf"], app=app, context=self.context
            )
        elif "siteconf" in self.context:
            siteconf = read_siteconf(
                self.context["siteconf"], app=app, context=self.context
            )
        else:
            siteconf = read_siteconf(app=app, context=self.context)

        if siteconf is None:
            raise Exception("Could not read siteconf")

        self.siteconf = siteconf

        # Load versionmap
        filename = testdata.get(
            "versionmap", self.get_file("%(ENRICH_ETC)s/versionmap.json")
        )
        timestamp, versionmap = read_versionmap(filename)
        self.versionmap = versionmap

        # => Load the data frames
        expand = os.path.expandvars
        defaultdir = self.get_file("%(ENRICH_TEST)s")

        self.data_root = expand(testdata.get("data_root", defaultdir))
        self.enrich_data_dir = self.data_root
        self.inputdir = expand(testdata.get("inputdir", self.data_root))
        self.outputdir = expand(testdata.get("outputdir", self.data_root))
        self.statedir = expand(testdata.get("statedir", self.data_root))

        # Insert global supported_extra_args
        if "global" in testdata:
            if "args" in testdata["global"]:
                args = testdata["global"]["args"]
                if not isinstance(args, dict):
                    raise Exception("Global args should be a dict")
                self.supported_extra_args = [
                    {
                        "name": k,
                        "description": "Global arg {}".format(k),
                        "required": False,
                        "default": v,
                    }
                    for k, v in args.items()
                ]

        testdata = testdata.get("data", {})
        for framename, details in testdata.items():
            stages = details.get("stages", [])
            frametype = details.get("frametype", "pandas")

            # We could have potentially specified multiple files that need to be loaded
            paths = []
            transform = details["transform"]
            sources = []
            if "source" in details:
                source = details["source"]
            else:
                source = details["filename"]
            if isinstance(source, str):
                if "inputdir" not in source:
                    source = "%(inputdir)s/%(transform)s/" + source
                sources.append(source)
                path = self.get_file(
                    source, extra={"inputdir": self.inputdir, "transform": transform}
                )
                paths.extend(glob.glob(path))
            elif isinstance(source, list):
                for f in source:
                    if "inputdir" not in f:
                        f = "%(inputdir)s/%(transform)s/" + f
                    sources.append(f)
                    path = self.get_file(
                        f, extra={"inputdir": self.inputdir, "transform": transform}
                    )
                    paths.extend(glob.glob(path))
            elif isinstance(source, dict):
                for group in source:
                    for f in source[group]:
                        sources.append(f)
                        path = self.get_file(
                            f, extra={"transform": transform, "group": group}
                        )
                        paths.extend(glob.glob(path))

            if len(paths) == 0:
                logger.warning(
                    "No files to load for {}".format(framename),
                    extra={"data": "Searched " + ",".join(sources)},
                )
                continue

            _dfs = []
            for path in paths:
                if not os.path.exists(path):
                    raise Exception("Missing input file: {}".format(path))

                if frametype in ["pandas"]:
                    params = details.get("params", {})
                    df = pd.read_csv(path, **params)
                elif frametype in ["dict"]:
                    params = {}
                    df = json.load(open(path, "r"))
                _dfs.append(df)

            # => Load them ..
            if len(_dfs) == 0:
                pass
            elif len(_dfs) == 1:
                df = _dfs[0]
            else:
                if "mergedf" not in details:
                    raise Exception("Please use 'mergedf' attribute to combine")

                df = details["mergedf"](_dfs)

            details = {
                "df": df,
                "frametype": frametype,
                "stages": stages,
                "transform": details["transform"],
                "history": [{"log": "Test load of data"}],
                "params": [
                    {
                        "type": "lineage",
                        "dependencies": [
                            {"type": "file", "usage": "input", "name": paths}
                        ],
                    }
                    # {
                    #    'type': 'export',
                    #    'params': params
                    # }
                ],
            }
            self.state.update_frame(framename, details)

        # => Load the runs
        runs = testdata.get("runs", [])
        self.runmanager.load_runs(runs, self.state)

    def store_test_state(self, obj, testdata=None):

        # Where should I store?
        if testdata is None:
            testdata = obj.testdata

        try:
            os.makedirs(self.statedir)
        except:
            pass

        metadata = json.dumps(
            {
                "name": self.name,
                "runid": self.state.runid,
                "notes": self.state.notes,
                "performance": self.state.performance_notes,
                "stats": self.state.stats,
                "start_time": self.state.start_time,
                "end_time": self.state.end_time,
                "pid": self.state.pid,
                "frames": self.state.state,
                "expectations": self.state.expectations,
                "accesses": self.accessed_files,
                "dataset_accesses": self.state.dataset_accesses,
                "versionmap": self.versionmap,
            },
            cls=CustomEncoder,
            indent=4,
        )

        path = os.path.join(self.statedir, "metadata.json")
        with open(path, "w") as fd:
            fd.write(metadata)

        frames = self.state.get_frame_list()
        for frame in frames:
            detail = self.state.get_frame(frame)

            # Parameters for export
            export = {
                "index": False,
            }

            for p in detail["params"]:
                if p.get("type", None) == "export":
                    export.update(p.get("params", {}))

            df = detail["df"]
            if df is None:
                continue

            frametype = detail["frametype"]
            if frametype in ["pandas", "spark"]:
                path = os.path.join(self.statedir, frame + ".csv")
                df.to_csv(path, **export)
            elif frametype in ["dict"]:
                path = os.path.join(self.statedir, frame + ".json")
                with open(path, "w") as fd:
                    fd.write(json.dumps(df, indent=4))

        return self.statedir

    def get_state(self):
        return self.state

    def add_notification_targets(self, targets):
        if "email" in targets:
            self.notifications["email"].extend(targets["email"])

    def get_credentials(self, name):

        siteconf = self.siteconf

        if ("credentials" not in siteconf) or (name not in siteconf["credentials"]):
            raise Exception("missing credentials")

        return siteconf["credentials"][name]

    def get_versionmap(self):
        return copy.copy(self.versionmap)


class MockPipeline:
    def execute(self, transformcls, testdata, save_state=False, context={}):

        # => First create a mock pipeline.
        config = MockConfig(context)

        # => Configure it...
        config_params = testdata.get("config", {})
        config.configure(config_params)

        # => Load test state
        config.load_test_state(testdata)

        # => Get the state object..
        state = config.get_state()

        # => Instantiate the transform...
        transform = transformcls(config=config)

        # => Configure
        conf = testdata.get("conf", {})
        transform.configure(conf)

        # => Validate the configuration
        transform.validate("conf", state)
        transform.validate("args", state)

        # => Now call the process
        transform.process(state)

        # => Now validate the output state
        transform.validate("results", state)

        # => Store the final resultant state
        if save_state:
            config.store_test_state(transform, testdata)
