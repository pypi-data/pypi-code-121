import os
import sys
import json
import copy
import logging
import traceback
import humanize
from datetime import datetime
from dateutil import parser as date_parser
import logging

logger = logging.getLogger("app")

###############################################################
# Run History
###############################################################
class Run(object):
    """
    A single instance of command run. This class will mediate
    access to the command logs and metadata.

    """

    def __init__(self, rundir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rundir = rundir
        self.runid = os.path.basename(self.rundir)
        epoch = datetime.fromtimestamp(0)
        self.start_time = epoch
        self.end_time = epoch

        try:
            filename = os.path.join(self.rundir, "metadata.json")
            self.metadata = json.load(open(filename))
            schema = self.metadata.get("schema", "unknown")
            command = self.metadata.get("command", {})

            for attr in [
                "host",
                "name",
                "status",
                "description",
                "cmdline",
                "message",
                "user",
                "runid",
                "start_time",
                "end_time",
            ]:

                if schema == "standalone:command":
                    if attr in command:
                        if attr in ["start_time", "end_time"]:
                            value = date_parser.parse(command[attr])
                        else:
                            value = command[attr]
                        setattr(self, attr, value)
                    elif attr == "user":
                        value = command["stats"]["user"]
                        setattr(self, attr, value)
                    elif attr == "user":
                        value = command["stats"]["user"]
                        setattr(self, attr, value)
                else:
                    if attr in ["start_time", "end_time"]:
                        value = date_parser.parse(self.metadata[attr])
                    elif attr == "user":
                        value = self.metadata.get("username", "unknown")
                    elif attr == "name":
                        value = self.metadata.get("command", "unknown")
                    else:
                        value = self.metadata.get(attr, "unknown")

                    # Rename one attribute
                    setattr(self, attr, value)

            self.outputs = self.metadata.get("outputs", [])
        except:
            traceback.print_exc()
            for attr in [
                "host",
                "name",
                "status",
                "description",
                "cmdline" "message",
                "user",
            ]:
                setattr(self, attr, "unknown")
            self.outputs = []

        logfile = self.metadata.get("log", "log.json")
        self.logfile = os.path.join(self.rundir, logfile)
        self.log = open(self.logfile).readlines()

        self.duration = (self.end_time - self.start_time).total_seconds()

    def __str__(self):
        return self.name

    @property
    def username(self):
        return self.user

    def get_command(self):
        return self.name.replace("enrichcmd run ", "").strip()

    def get_cmdline(self):
        cmdline = copy.copy(self.cmdline)
        if cmdline[0].endswith("enrichcmd"):
            cmdline[0] = "enrichcmd"
        return " ".join(cmdline)


class RunManager(object):
    """
    Command Run Management to enable access to
    pass runs of the commands.

    """

    def __init__(self, conf, *args, **kwargs):
        """

        Args:
            conf (dict): Only one parameter supported now 'command_root'
        """
        super().__init__(*args, **kwargs)
        self.runs = []
        self.conf = conf

        if "command_root" in conf:
            command_roots = [conf["command_root"]]
        elif "command_roots" in conf:
            command_roots = conf["command_roots"]
        else:
            raise Exception(
                "Configuration should specify command_root or command_roots parameters"
            )

        self.command_roots = []
        for p in command_roots:
            self.command_roots.append(os.path.abspath(p))

        # Collect rundirs from all directories...
        rundirs = []
        for p in self.command_roots:
            if not os.path.exists(p):
                logger.debug("Invalid command root directory: {}".format(p))
                continue

            rundirs.extend(
                [{"name": d, "path": os.path.join(p, d)} for d in os.listdir(p)]
            )

        rundirs = sorted(rundirs, key=lambda r: r["name"], reverse=True)

        count = conf.get("history", 100)
        rundirs = rundirs[:count]
        errors = []
        for r in rundirs:
            try:
                runid = r["name"]
                rundir = r["path"]
                self.runs.append(Run(rundir))
            except:
                traceback.print_exc()
                errors.append(runid)

        if len(errors) > 0:
            logger.debug(
                "Found errors while loading command history",
                extra={"transform": "Commands", "data": str(errors)},
            )

    def get_runs(self, username=None):
        """
        Get runs for a given username
        """

        runs = [r for r in self.runs if ((username is None) or (r.user == username))]
        return runs

    def get_run(self, runid):

        run = None
        for p in self.command_roots:
            rundir = os.path.join(p, runid)
            if os.path.exists(rundir):
                try:
                    run = Run(rundir)
                except:
                    pass

        return run

    def show_history(self, n=10):

        runs = sorted(self.runs, key=lambda r: r.start_time, reverse=True)

        template = "{:10s}{:30s}{:10s}{:15s}{:20s}"
        print(template.format("Who", "Description", "Status", "When", "Name"))
        for r in runs[:n]:
            print(
                template.format(
                    r.user,
                    r.description[:27],
                    r.status[:10],
                    humanize.naturaltime(r.start_time),
                    r.name,
                )
            )
