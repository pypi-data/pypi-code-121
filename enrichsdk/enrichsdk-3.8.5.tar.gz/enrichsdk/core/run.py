"""
Classes to handle run-metadata

"""
import os
import sys
import json
import copy
import platform
import traceback
import importlib
import csv
from dateutil import parser as dateparser
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger("app")


class RunBase(object):
    """
    Base class for loading each run
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Run class

        Args:
            config (object): Pipeline execution object
            rundir (str): Directory with runs

        """
        self.config = kwargs.pop("config")
        self.rundir = kwargs.pop("rundir")

        if not os.path.exists(self.rundir):
            raise Exception("missing rundir")

        self.files = []
        self.name = "Unknown"
        self.runid = "Unknown"
        self.load_time = datetime.now()
        self.deleted = False

    def __str__(self):
        return "{}.{}".format(self.name, self.runid)

    def load_metadata(self):
        """
        Load run metadata for a given rundir

        This will not load if the metadata size is more than
        1MB as a way to do sanity check.

        """
        metadatapath = os.path.join(self.rundir, "metadata.json")
        if not os.path.exists(metadatapath):
            raise Exception("Could not locate metadata.json")

        statinfo = os.stat(metadatapath)
        if statinfo.st_size > 1024 * 1024:  # 1MB
            raise Exception("Metadata file size too large")

        metadata = json.loads(open(metadatapath).read())
        self.metadata = metadata

        schema = metadata.get("schema", "standard:pipeline")
        if schema not in ["standard:pipeline", "standard:task"]:
            raise Exception("Unknown run metadata structure")

        # Initialize some values. Have to switch to getattr
        self.start_time = dateparser.parse(metadata["start_time"])
        self.end_time = dateparser.parse(metadata["end_time"])

        duration = self.end_time - self.start_time
        self.duration = (
            duration.days * 86400 + duration.seconds + 1000 * duration.microseconds
        )

        self.status = metadata["status"]
        self.name = metadata["name"]
        config = metadata.get("config", {})
        self.display = metadata.get("display", config.get("display", self.name))
        self.description = metadata["description"]
        self.computation = metadata.get("computation", "batch")
        self.runid = metadata["runid"]
        self.scheduled = metadata["scheduled"]
        self.uid = metadata["uid"]
        self.stats = metadata["stats"]
        self.pid = metadata.get("pid", None)
        self.cmdline = metadata.get("cmdline", [])
        self.lineage = []

        # Patch for backward compatability
        if ("platform" in self.stats) and ("name" in self.stats["platform"]):
            self.stats["platform"]["node"] = self.stats["platform"]["name"]

    def compute_lineage(self):
        """
        Compute lineage from the metadata
        """
        last = {}  # what is the last touch of a dataframe
        nodes = {}
        edges = []

        metadata = self.metadata
        if "details" not in metadata:
            return

        # => First collect the entries
        allentries = []
        for framename in metadata["details"]:

            details = metadata["details"][framename]
            description = details.get("description", "")

            ######################
            # => Sanity check...
            ######################
            if ("params" not in details) or (not isinstance(details["params"], list)):
                logger.error(
                    "Could not read params in metadata for {} in run {} metadata".format(
                        framename, self.name
                    )
                )
                continue

            params = details["params"]

            # Params is a list of inputs and outputs associated with the file.
            entries = [
                copy.copy(p) for p in params if (p.get("type", "unknown") == "lineage")
            ]

            # Insert frame and description...
            for e in entries:
                e["frame"] = framename
                e["description"] = description

                # Insert timestamp if missing
                if "timestamp" not in e:
                    if self.end_time is not None:
                        e["timestamp"] = self.end_time.timestamp()
                    else:
                        e["timestamp"] = self.start_time.timestamp()

            # Append to the global list.
            allentries.extend(entries)

        # => If there are any
        if len(allentries) == 0:
            return

        # => Now process the entries...
        allentries = sorted(allentries, key=lambda entry: entry["timestamp"])

        for p in allentries:

            framename = p["frame"]
            transform = p.get("transform", "unknown")

            # => Anchor node
            core = "{} ({})".format(framename, transform)
            if core not in nodes:
                nodes[core] = {
                    "id": core,
                    "label": core.replace(" ", "\n"),
                    "type": "dataframe",
                    "text": "Dataframe\n" + p["description"],
                }

            dependencies = p.get("dependencies", [])
            if len(dependencies) == 0:
                continue

            for d in dependencies:

                nature = d.get("nature", "unknown").lower().strip()
                type_ = d.get("type", "unknown").lower().strip()

                if type_ in ["column", "columns"]:
                    continue

                objects = d.get("objects", d.get("name", []))
                if not isinstance(objects, list) and not isinstance(objects, dict):
                    continue

                # Now clean and organize the dependencies...
                """
                    1. dependencies = [path1, path2..]
                    2. dependencies = {
                        "source1": path1,
                        "source2": description2
                    }
                    3. dependencies = {
                          "source1": {
                             "transform": "Trial",
                             "text": "...loan-s3/..."
                           }
                    }
                """
                cleaned_objects = {}
                if isinstance(objects, list):
                    # A list of files/text items
                    for o in objects:
                        label = os.path.basename(o) if "/" in o else o
                        cleaned_objects[label] = {
                            "transform": transform,
                            "text": str(o),
                        }
                elif isinstance(objects, dict):
                    for o, detail in objects.items():
                        # A dictionary of name: <object>
                        if isinstance(detail, str):
                            # A dictionary of name: str
                            cleaned_objects[o] = {
                                "transform": transform,
                                "text": detail,
                            }
                        elif isinstance(detail, str):
                            # A dictionary of name: list
                            cleaned_objects[o] = {
                                "transform": transform,
                                "text": ",".join([str(s) for s in detail]),
                            }
                        elif isinstance(detail, dict):
                            # A dictionary of name: dict
                            node_transform = detail.get("transform", transform)
                            if "text" in detail:
                                text = detail["text"]
                            else:
                                detail.pop("transform", None)
                                text = str(detail)
                            cleaned_objects[o] = {
                                "transform": node_transform,
                                "text": text,
                            }

                for label, detail in cleaned_objects.items():
                    generator = detail["transform"]
                    text = detail["text"]
                    node = "{} ({})".format(label, generator)

                    if type_ in ["file"]:
                        text = "Path/other: {}".format(text)
                    elif type_ in ["dataframe", "dataframes"]:
                        type_ = "dataframe"
                        node_transform = last.get(label, generator)
                        node = "{} ({})".format(label, node_transform)
                        text = "Dataframe: {}".format(text)
                    elif type_ in ["database", "db", "databases"]:
                        type_ = "database"
                        node_transform = last.get(label, generator)
                        node = "{} ({})".format(label, node_transform)
                        text = "DB: {}".format(text)
                    elif type_ in ["api", "url"]:
                        type_ = "url"
                        node_transform = last.get(label, generator)
                        node = "{} ({})".format(label, generator)
                        text = "URL: {}".format(text)
                    elif type_ in ["columns", "column"]:
                        continue
                    else:
                        logging.warning("Unknown Type: {}".format(type_))
                        continue

                    # => Target node..
                    if node not in nodes:
                        nodes[node] = {
                            "id": node,
                            "label": node.replace(" ", "\n"),
                            "type": type_,
                            "text": text,
                        }

                    # => Add edge
                    source = core if nature == "output" else node
                    target = node if nature == "output" else core
                    edge = {
                        "id": "link{}".format(len(edges) + 1),
                        "source": source,
                        "target": target,
                    }

                    edges.append(edge)

            # => Keep track of what needs to be done.
            last[framename] = transform

        self.lineage = list(nodes.values()) + edges

    def get_lineage(self):
        """
        Return lineage in a way that it can be rendered by
        cytoscape.
        """
        return [{"data": l} for l in self.lineage]

    def load(self):
        """
        Load the metadata and compute lineage
        """
        self.load_metadata()
        try:
            self.compute_lineage()
            # lineage = self.get_lineage()
            # if len(lineage) > 0:
            #    print(json.dumps(lineage, indent=4))
        except:
            logger.exception("Unable to compute lineage for {}".format(str(self)))

    def compute_compliance_metadata(self):
        """
        Collect the column information from each of the frames adnd generate
        """
        frames = {}

        metadata = self.metadata
        if "details" not in metadata:
            return frames

        # => First collect the entries
        for framename in metadata["details"]:
            """
            For each frame collect lineage and column information
            """

            details = metadata["details"][framename]
            description = details.get("description", "")
            frametype = details.get("frametype", "unknown")

            if ("params" not in details) or (not isinstance(details["params"], list)):
                continue

            params = details["params"]

            # First check the finalized columns...
            columns_output = None
            columns_default = None
            inputs = {}
            outputs = {}

            for p in params:
                if not isinstance(p, dict):
                    continue
                _type = p.get("type", None)
                _action = p.get("action", None)
                _columns = p.get("columns", None)

                # => Have columns been specified, then use it.
                if _type == "compute":
                    # Extract column information
                    if (isinstance(_columns, dict)) and (len(_columns) > 0):
                        if _action == "output":
                            columns_output = _columns
                        else:
                            columns_default = _columns

                # Now collect information from lineage metadata
                if _type == "lineage":

                    # Extract lineage information
                    dependencies = p.get("dependencies", [])
                    for d in dependencies:
                        nature = d.get("nature", "unknown").lower().strip()
                        type_ = d.get("type", "unknown").lower().strip()

                        if type_ in ["dataframe", "columns"]:
                            continue

                        # Dependencies can be specified as a
                        # (a) a list
                        # (b) a dict: name => str
                        # (c) a dict: name => list
                        # (d) a dict: name => dict
                        objects = d.get("objects", {})
                        if isinstance(objects, list):
                            for name in objects:
                                if not isinstance(name, str):
                                    continue
                                if nature == "input":
                                    if name not in inputs:
                                        inputs[name] = name
                                    else:
                                        inputs[name] += " " + name
                                else:
                                    if name not in outputs:
                                        outputs[name] = name
                                    else:
                                        outputs[name] += " " + name
                        elif isinstance(objects, dict):
                            for name, desc in objects.items():
                                if isinstance(desc, list):
                                    desc = "; ".join(desc)
                                if nature == "input":
                                    if name not in inputs:
                                        inputs[name] = desc
                                    else:
                                        inputs[name] += " " + desc
                                else:
                                    if name not in outputs:
                                        outputs[name] = desc
                                    else:
                                        outputs[name] += " " + desc

            # If column information has been collapsed, then use
            # it. Otherwise use the default column information
            if columns_output is not None:
                columns = columns_output
            else:
                columns = columns_default

            # => Now collect all the information in a single dict We
            # know for each frame, what the columns are, what was the
            # input and what was the output.
            frames[framename] = {
                "framename": framename,
                "frametype": frametype,
                "description": description,
                "type": frametype,
                "columns": columns,
                "inputs": inputs,
                "outputs": outputs,
            }

        return frames

    def generate_compliance_summary(self):
        """
        Look through the dataframe metadata and
        lineage to determine
        """

        # Now we have to gather the columns
        frames = self.compute_compliance_metadata()

        summary = defaultdict(list)
        for frame in frames.values():

            # Consider only the outputs. Ignore the inputs
            # Each flow entry is <name-of-output> -> Text
            flows = list(frame["outputs"].items())

            # => Collapse the information. There could potentially be multiple entries. How?
            io = {}
            for k, v in flows:
                if k not in io:
                    io[k] = []
                if isinstance(v, str):
                    io[k].append(v)
                elif isinstance(v, list):
                    io[k].extend(v)
                else:
                    io[k].append(str(v))

            for inputname, desc in io.items():
                if isinstance(desc, list):
                    desc = ". ".join(desc)
                if ("columns" not in frame) or (frame["columns"] is None):
                    continue
                for colname, coldetails in frame["columns"].items():
                    coldetails = copy.copy(coldetails)
                    coldetails["source_name"] = inputname
                    coldetails["source_description"] = desc + " " + frame["description"]
                    coldetails["source_format"] = frame["frametype"]
                    coldetails["column"] = colname
                    label = (inputname, colname)
                    summary[label].append(coldetails)

        # flatten list of coldetails...
        values = []
        for sublist in summary.values():
            for item in sublist:
                values.append(item)

        return values

    def load_files(self, include_output_frame=True):
        """
        Minimal loading of files
        """

        metadata = self.metadata
        if "details" not in metadata:
            # Nothing to be done
            return

        for framename in metadata["details"]:

            details = metadata["details"][framename]

            ######################
            # => Sanity check...
            ######################
            if ("params" not in details) or (not isinstance(details["params"], list)):
                logger.error(
                    "Could not read params in metadata for {} in run {} metadata".format(
                        framename, self.name
                    )
                )
                continue

            if "history" not in details:
                logger.error(
                    "Could not read history in metadata for {} in run {} metadata".format(
                        framename, self.name
                    )
                )
                continue

            params = details["params"]
            history = details["history"]

            # Params is a list of inputs and outputs associated with the file.
            for p in params:

                if p.get("action", "unknown") != "output":
                    continue

                # Now we have params corresponding to a file write
                # action. Do we have a valid filename?
                if (
                    ("filename" not in p)
                    or (not isinstance(p["filename"], str))
                    or (len(p["filename"]) == 0)
                ):
                    continue

                # A given frame can have multiple components, e.g.,
                # multiple partitions.
                if (
                    ("components" not in p)
                    or (not isinstance(p["components"], list))
                    or (len(p["components"]) == 0)
                ):
                    continue

                # Get the first component only for simplicity
                component = p["components"][0]

                # Component looks like this...
                {
                    "filename": "acme/PLP/output/PLPTarget/plptarget-20191002-165551/product_persona.csv",
                    "modified_time": "Wed Oct 2 16:58:25 2019",
                    "sha256sum": "e9731bdc22f545da71304e77d50da31ccb263458317a2c1b7b73177092ad5d73",
                    "columns": 2,
                    "filesize": "0.000 MB",
                    "create_time": "Wed Oct 2 16:58:25 2019",
                    "rows": 1,
                }

                root = self.config.enrich_data_dir
                path = os.path.join(root, component["filename"])
                if not os.path.exists(path):
                    path = component["filename"]
                frametype = p.get("frametype", "pandas")

                detail = copy.copy(component)
                detail.update(
                    {
                        "name": framename,
                        "label": framename,
                        "path": path,
                        "frametype": frametype,
                    }
                )

                self.files.append(detail)

    def get_files(self):
        """
        Get the files loaded for this run

        Returns:
               files (list): List of dictionaries
        """
        return self.files

    def get_cmdline(self):
        """
        Get the cleaned command line used to generate the run
        """
        enrich_root = os.environ["ENRICH_ROOT"]
        cmdline = self.cmdline
        cleaned = []
        for c in cmdline:
            if ".virtualenvs" in c:
                cleaned.append(
                    "..." + c[c.index(".virtualenvs") + len(".virtualenvs") + 1 :]
                )
            elif c.startswith(enrich_root):
                cleaned.append("..." + c[len(enrich_root) + 1 :])
            else:
                cleaned.append(c)

        return cleaned

    def get_extra_args(self):
        """
        Get the extra args specified for this run
        """
        enrich_root = os.environ["ENRICH_ROOT"]
        cmdline = self.cmdline
        extra = {}
        for c in cmdline:
            if ":" not in c or "=" not in c:
                continue

            module = c[: c.index(":")]
            name = c[c.index(":") + 1 : c.index("=")]
            value = c[c.index("=") + 1 :]

            if module not in extra:
                extra[module] = []
            extra[module].append({"name": name, "value": value})
        return extra

    def get_run_note(self):
        """
        Get any note given on the command line..
        """
        extra_args = self.get_extra_args()
        for arg in extra_args.get("global", []):
            if arg["name"] == "note":
                return arg["value"]

        return ""


class RunManagerBase(object):
    """
    Load and keep all the runs ready
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Run Manager

        Args:

             config (object): Pipeline execution object
             numruns (int): Number of runs to load

        """

        self.config = kwargs.pop("config")
        self.runs = []
        self.runcls = RunBase
        self.numruns = kwargs.get("numruns", 100)

    def load_one_run(self, outputdirs, runid):

        # Check if already present. If so, nothing to be done
        run = self.get_run(runid)
        if run is not None:
            run.load()
            return

        logger.debug(
            "RunID ({})missing in cache. Loading".format(runid),
            extra={"transform": self.config.name},
        )
        rundir = None
        for outputdir in outputdirs:
            if runid in os.listdir(outputdir):
                rundir = os.path.join(outputdir, runid)
                break

        # Nothing to be done...
        if rundir is None:
            logger.error(
                "RunID ({}) could not be found".format(runid),
                extra={
                    "transform": self.config.name,
                    "data": "Output dir(s): {}".format(", ".join(outputdirs)),
                },
            )
            return

        try:
            run = self.runcls(config=self.config, name=runid, rundir=rundir)
            run.load()
            self.runs.append(run)
            logger.debug(
                "Loaded a new run: {}".format(runid),
                extra={
                    "transform": self.config.name,
                },
            )
        except:
            logger.exception(
                "Unable to load runid: {}".format(runid),
                extra={
                    "transform": self.config.name,
                },
            )
        return

    def load(self, offset=0, page=50, runid=None):
        """
        Load the runs

        Args:

             offset: offset from the last run
             page: number of runs per page
             runid: arbitrary runid (overrides the offset and page

        """

        # Default
        outputdirs = [self.config.outputdir]

        # Check if there is an archive (e.g., s3 mounted on a
        # path). If if exists then include it.
        backupconfig = self.config.siteconf.get("backup", {})
        mountroot = backupconfig.get("mount", None)
        if mountroot is not None:
            relpath = os.path.relpath(self.config.outputdir, self.config.enrich_root)
            mountdir = os.path.join(mountroot, relpath)
            if os.path.exists(mountdir):
                outputdirs.append(mountdir)

        if runid is not None:
            return self.load_one_run(outputdirs, runid)

        extra = 10
        run_cache = {r.runid: r for r in self.runs}
        self.runs = []

        runids = []
        count = 0
        for outputdir in outputdirs:

            # => Check if the output dir exists
            if not os.path.exists(outputdir):
                continue

            # Default path where no run id is specified. If we have
            # not seen the outputdir, then include it.
            for runid in sorted(os.listdir(outputdir), reverse=True):
                if runid not in runids:
                    runids.append(
                        {"runid": runid, "rundir": os.path.join(outputdir, runid)}
                    )
                    count += 1

                # Dont read much more...
                if count > offset + page + extra:
                    break

        errors = []
        for r in runids:
            if self.config.runid == r["runid"]:
                # Dont read the current run's information. It wont be
                # there.
                continue

            runid = r["runid"]
            rundir = r["rundir"]

            # Get timestamp of the file.
            logfile = os.path.join(rundir, "log.json")
            if not os.path.exists(logfile):
                continue

            try:
                mtime = os.path.getmtime(logfile)
            except:
                mtime = 0

            last_modified_date = datetime.fromtimestamp(mtime)

            # See if we have the latest copy. If so use it.
            if (runid in run_cache) and (
                run_cache[runid].load_time > last_modified_date
            ):
                self.runs.append(run_cache[runid])
                continue

            # If it doesnt exist or the cope is not recent, the load it.
            try:
                run = self.runcls(config=self.config, name=runid, rundir=rundir)
                run.load()
                self.runs.append(run)
            except Exception as e:
                errors.append(str(r) + ": " + str(e))
                pass

        # Now that all the runs are loaded, sort them..
        self.runs = sorted(self.runs, key=lambda r: r.start_time, reverse=True)

        logger.debug(
            "Loaded {} past runs".format(len(self.runs)),
            extra=self.config.get_extra(
                {
                    "transform": self.config.name,
                    "data": str(list([r.runid for r in self.runs])),
                }
            ),
        )
        if len(errors) > 0:
            logger.error(
                "Error while load {} past runs".format(len(errors)),
                extra=self.config.get_extra(
                    {"transform": self.config.name, "data": errors}
                ),
            )

    def get_run(self, runid):
        """
        Get run object for a given runid

        Args:

             runid (str): Run id

        """

        for r in self.runs:
            if r.runid == runid:
                return r

        return None

    def get_last_run(self, status="success"):
        """
        Get the last run with a given status

        if status is None or '' then return the
        last run irrespective of the status.

        Args:

             status (str): Status of the tune

        """
        for r in self.runs:
            if status in [None, "any", "*", ""]:
                return r

            if r.status == status and not r.deleted:
                return r
        return None

    def refresh(self):
        """
        Reload all the runs
        """
        self.runs = {}
        self.load()


class PipelineConfig(object):
    """
    Pipeline class. Simulates the pipeline execution
    service's internal object.
    """

    def __init__(self, conf):
        self.spec = conf
        self.name = conf["name"]
        self.runid = "unknown"
        self.siteconf = {}
        self.set_params()

    def __str__(self):
        return self.name

    def set_params(self):

        # Set parameters
        params = {
            "name": self.spec["name"],
            "enrich_root": os.environ["ENRICH_ROOT"],
            "enrich_run_root": os.environ.get(
                "ENRICH_RUN_ROOT", os.environ["ENRICH_ROOT"]
            ),
            "enrich_customers_dir": os.environ["ENRICH_CUSTOMERS"],
            "enrich_data_dir": os.environ["ENRICH_DATA"],
        }

        for attr in ["data_root", "output"]:
            params[attr] = self.spec[attr] % params

        # => handle usecase_root/customer_root carefully for backward compatability
        usecase_root = self.spec.get(
            "usecase_root", self.spec.get("customer_root", "Unknown")
        )
        params["usecase_root"] = params["customer_root"] = usecase_root % params

        # Handle aliases
        aliases = {
            "outputdir": "output",
            "enrich_customers": "enrich_customers_dir",
            "enrich_data": "enrich_data_dir",
        }
        for k, v in aliases.items():
            params[k] = params[v]

        # Store them both as a
        self.params = params
        for k, v in self.params.items():
            setattr(self, k, v)

    def get_extra(self, extra):
        # Insert any additional attributes. Nothing as of now.
        return extra


def get_pipeline(path):
    """
    Take the given path and turn that into config. This
    function instantiates a PipelineConfig object and
    assigns it a run manager

    """
    try:
        if path.lower().endswith(".json"):
            confobj = json.load(open(path))
            confobj["conf"] = path
        else:
            # Load python
            modname = "".join([x if x.isalnum() else "_" for x in path])
            modspec = importlib.util.spec_from_file_location(modname, path)
            mod = importlib.util.module_from_spec(modspec)
            modspec.loader.exec_module(mod)
            if not hasattr(mod, "config"):
                raise Exception("Invalid pipeline configuration path")
            confobj = mod.config
            confobj["conf"] = path
    except:
        logger.exception("Unable to load specified pipeline configuration")
        raise

    # => Now we have a dictionary of the configuration.
    config = PipelineConfig(confobj)

    # Add run manager
    config.runmanager = RunManagerBase(config=config)

    # Return
    return config
