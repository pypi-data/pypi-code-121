import os
import sys
import json
import logging
from datetime import datetime
import platform
import distro
import getpass
import logging
from collections import OrderedDict
import logging

from . import log

logger = logging.getLogger("app")


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)


#######################################################
# Config object to handle a number of helper functions
#######################################################
class Config(object):
    """
    Context object having a number of capabilities including
    log management, files and path management, credentials
    lookup etc.

    """

    def __init__(self, params, *args, **kwargs):
        """
        Initialize the config (context) object.

        Args:
          params (dict): Only two keys are supported. debug (bool) prints
                         extra information. It is useful for debugging loading.
                         settings is the path to the settings file.
        """
        super().__init__(*args, **kwargs)
        self.debug = params.get("debug", False)
        self.settings = params.get("settings", None)
        self.readonly = params.get("readonly", False)
        self.show_metadata = params.get("show_metadata", True)

        if self.settings is not None:
            self.settings = os.path.expanduser(self.settings)

        self.now = datetime.now()
        self.conf = {"credentials": {}, "libraries": []}
        self.stats = {
            "platform": {
                "node": platform.node(),
                "os": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "python": platform.python_version(),
                "distribution": distro.linux_distribution(),
            },
            "user": getpass.getuser(),
        }

        self.state = self.get_default_metadata()
        self.state.update({"outputs": [], "notes": [], "message": ""})

    def get_default_metadata(self):
        """
        Get reusable metadata dict with some standard fields.
        """
        metadata = {
            "schema": "standalone:command",
            "version": "1.0",
            "timestamp": datetime.now().replace(microsecond=0).isoformat(),
            "command": {
                "name": "Unknown",
                "status": "initial",
                "description": "",
                "host": self.stats["platform"]["node"],
                "stats": self.stats,
                "pid": os.getpid(),
                "start_time": self.now,
                "end_time": self.now,
                "cmdline": list(sys.argv),
            },
        }

        return metadata

    def configure(self, settings=None):
        """
        Configure the config object

        Args:
           settings (str): Path to the settings file

        """
        if settings is None:
            settings = self.settings

        if (settings is None) or (not os.path.exists(settings)):
            # Quietly return. Do nothing..
            raise Exception("Settings path invalid or undefined: {}".format(settings))

        try:
            loaded_conf = json.load(open(settings))
        except:
            logger.exception("Invalid settings file")
            loaded_conf = None

        if loaded_conf is None:
            return

        # Materialize the paths...
        self.enrich_root = loaded_conf.get("enrich_root")
        self.enrich_root = os.path.expanduser(self.enrich_root)
        self.enrich_root = os.path.abspath(self.enrich_root)

        libraries = loaded_conf.get("libraries", [])
        libraries = [self.get_file(l) for l in libraries]
        self.conf["libraries"] = libraries

        # Insert the rest
        defaults = {
            "enrich_data": "%(enrich_root)s/data",
            "enrich_customers": "%(enrich_root)s/customers",
            "runid": "run-%Y%m%d-%H%M%S-%(user)s",
            "command_root": "%(enrich_data)s/_commands",
            "rundir": "%(command_root)s/%(hostname)s/%(runid)s",
            "outputdir": "%(rundir)s/output",
            "log": "%(rundir)s/log.json",
            "metadata": "%(rundir)s/metadata.json",
            "args": {},
        }

        for name in [
            "enrich_data",
            "enrich_customers",
            "runid",
            "command_root",
            "rundir",
            "outputdir",
            "log",
            "metadata",
        ]:
            default = defaults[name]
            try:
                final = loaded_conf.get(name, default)
                final = self.get_file(final)
            except:
                error = "Could not resolve: {} ({})".format(name, final)
                raise Exception(error)

            setattr(self, name, final)
            self.state["command"][name] = final

        for name in ["args"]:
            default = defaults[name]
            try:
                final = loaded_conf.get(name, default)
            except:
                error = "Could not resolve: {} ({})".format(name, final)
                raise Exception(error)

            setattr(self, name, final)

        # Set environment variables.....
        os.environ["ENRICH_ROOT"] = self.enrich_root
        os.environ["ENRICH_CUSTOMERS"] = self.enrich_customers
        os.environ["ENRICH_DATA"] = self.enrich_data

    def get_file(self, path):
        """
        Resolve the abstract specification into a full path

        Args:
           path (str): Path specification

        Example::

           %(enrich_data)/acme/Projects/commands

        This is resolved into `/home/ubuntu/enrich/data/acme/Projects/commands`

        """
        path = path.replace("%(", "%%(")  # This will make the strftime handling safe
        path = self.now.strftime(path)
        path = path % {
            "enrich_root": self.enrich_root,
            "enrich_data": getattr(self, "enrich_data", ""),
            "enrich_customers": getattr(self, "enrich_customers", ""),
            "user": self.stats["user"],
            "username": self.stats["user"],
            "hostname": self.stats["platform"]["node"],
            "node": self.stats["platform"]["node"],
            "runid": getattr(self, "runid", ""),
            "rundir": getattr(self, "rundir", ""),
            "outputdir": getattr(self, "outputdir", ""),
        }
        return path

    def get_relative_path(self, path, what="enrich_root"):

        if what == "enrich_root":
            return os.path.relpath(path, self.enrich_root)
        elif what == "enrich_data":
            return os.path.relpath(path, self.enrich_data)
        else:
            raise Exception("relative path should specify the root")

    def add_output(self, params):
        """
        Add file to the command output

        Args:
           params (dict): file parameters
              File parameters includes a name of the output, relative path
              to the file, and a description for the output

        """
        required = ["name", "description", "path"]
        missing = [n for n in required if n not in params]
        if len(missing) > 0:
            raise Exception("Missing parameters for the output: {}".format(missing))

        if os.path.isabs(params["path"]):
            raise Exception(
                "Path specified for output {} should be relative".format(params["name"])
            )

        for o in self.state["outputs"]:
            if o["name"] == params["name"]:
                raise Exception(
                    "An output already exists with the name: {}".format(params["name"])
                )

        params["fullpath"] = self.get_file("%(outputdir)s/{}".format(params["path"]))
        params["relpath"] = self.get_relative_path(params["fullpath"])

        # Now append
        self.state["outputs"].append(params)

    def get_output_handle(self, name, *args):
        """
        Get a file descriptor to the named output.

        Args:
           name (str): Name of the output.
              This output was previously added using `add_output` call.

        """
        for o in self.state["outputs"]:
            if o["name"] == name:
                try:
                    os.makedirs(os.path.dirname(o["fullpath"]))
                except:
                    pass
                return open(o["fullpath"], *args)

        raise Exception("Could not find output {}".format(name))

    def get_library_paths(self):
        return self.conf["libraries"]

    def get_args(self, cmd):
        """
        Get default arguments to the command specified in the settings file

        Args:
           cmd (str): Name of the command

        """
        logger = logging.getLogger("app")
        if not hasattr(self, "args"):
            if self.debug:
                logger.error("args not present")
            return {}

        if not isinstance(self.args, dict):
            if self.debug:
                logger.error("args not a dictionary")
            return {}

        return self.args.get(cmd, {})

    # Update the state
    def set_status(self, value):
        self.state["command"]["status"] = value

    def set_message(self, value):
        self.state["message"] = value

    def dump_state(self):

        # Update file statistics
        for o in self.state["outputs"]:
            path = o["fullpath"]
            st = os.stat(path)
            o["size"] = st.st_size

        metadata = OrderedDict(
            [
                ("schema", self.state["schema"]),
                ("version", self.state["version"]),
                ("timestamp", self.state["timestamp"]),
                ("command", self.state["command"]),
                ("message", self.state["message"]),
                ("outputs", self.state["outputs"]),
                ("notes", self.state["notes"]),
                ("log", os.path.relpath(self.log, self.rundir)),
            ]
        )

        if not self.readonly:
            with open(self.metadata, "w") as fd:
                json.dump(metadata, fd, indent=4, cls=CustomEncoder)
        elif self.show_metadata:
            print(json.dumps(metadata, indent=4, cls=CustomEncoder), file=sys.stderr)

        if self.debug:
            logger.debug("Dumped execution metadata")

    # Logging start and end
    def start_run(self, cmd):

        # Override with parameters from settings
        if not self.readonly:
            args = self.get_args(cmd)
            self.readonly = args.get("readonly", self.readonly)
            self.show_metadata = args.get("show_metadata", self.show_metadata)

        # Setup logging
        if self.readonly:
            log.logging_start()
        else:
            log.logging_start(self.log)

        logger = logging.getLogger("app")
        if self.debug:
            logger.debug("Starting run")

        # Dump the state at the beginning
        self.dump_state()

    def end_run(self):

        self.state["command"]["end_time"] = datetime.now()
        self.dump_state()

        # Dump status
        logger = logging.getLogger("app")

        if self.debug:
            logger.debug("Ending run")
        log.logging_end()
