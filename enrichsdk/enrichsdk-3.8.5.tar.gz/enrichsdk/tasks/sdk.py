"""
Set of predefined tasks
"""

import os
import pytz
import gzip
import re
import json
import datetime
import requests
import subprocess
import platform
import logging
from enrichsdk.tasks import Task

logger = logging.getLogger("app")

__all__ = ["BackupCoreTask", "SyncLocalCoreTask"]


class CloudMixin(object):
    def get_params(self):

        # resolve the destination
        now = self.config.now()
        params = {
            "node": platform.node(),
            "date": now.strftime("%Y-%m-%d"),
            "datetime": now.strftime("%Y%m%d-%H%M%S"),
        }
        return params

    def validate_args_cloud(self, what, state):

        dirspecs = self.dirspecs
        args = self.args

        fail = False
        msg = ""

        if "aws" not in args and "gcp" not in args:
            fail = True
            msg += "Both 'aws' or 'gcp' are missing. One is required\n"

        if "aws" in args:
            for v in ["credentials", "bucket"]:
                if v not in args["aws"]:
                    fail = True
                    msg += "Element '{}' is missing in aws config\n".format(v)

            try:
                cred = self.get_credentials(args["aws"]["credentials"])

                if ("access_key" not in cred) or ("secret_key" not in cred):
                    fail = True
                    msg += "Invalid S3 credentials. Missing access_key or secret_key\n"

            except Exception as e:
                fail = True
                msg += str(e) + "\n"

        elif "gcp" in args:
            for v in ["boto", "bucket"]:
                if v not in args["gcp"]:
                    fail = True
                    msg += "Element '{}' is missing in gcp config\n".format(v)

        # => Now check the backup/sync specification
        if (dirspecs not in args) or (not isinstance(args[dirspecs], list)):
            fail = True
            msg += "Element '{}' is missing or invalid (not a list)\n".format(dirspecs)
        else:
            for d in args[dirspecs]:
                if not isinstance(d, dict):
                    fail = True
                    msg += "Specification is not a dict: {}".format(d)
                    continue
                if "src" not in d or "dst" not in d:
                    fail = True
                    msg += "Specification should have src and dst"

        return fail, msg

    def validate_args(self, what, state):
        """
        Validate args.

        Looks like 'aws' and 'backupdirs' specification

        Example::

            "args": {
                 "backupdirs": [
                    {
                        "enable": true,
                        "name": "Logs",
                        "src": "%(enrich_root)s/logs/",
                        "dst": "backup/logs/"
                     },
                                ...
                  ],
                  "aws": {
                      "credentials": "enrich-acme",
                      "bucket": "client-enrich"
                  }
            }

        """
        args = self.args

        # Check
        fail, msg = self.validate_args_cloud(what, state)

        if fail:
            logger.error(
                "Invalid configuration",
                extra=self.config.get_extra({"transform": self.name, "data": msg}),
            )
            raise Exception("Invalid configuration")

    def get_env(self):
        """
        Get environment for the cloud provider
        """

        args = self.args
        env = dict(os.environ)
        if "aws" in args:
            cred = self.get_credentials(args["aws"]["credentials"])
            if cred is not None:
                if ("access_key" in cred) and (isinstance(cred["access_key"], str)):
                    env["AWS_ACCESS_KEY_ID"] = cred["access_key"]
                if ("secret_key" in cred) and (isinstance(cred["secret_key"], str)):
                    env["AWS_SECRET_ACCESS_KEY"] = cred["secret_key"]
        else:
            env["BOTO_CONFIG"] = self.config.get_file(args["gcp"]["boto"])

        env["TZ"] = args.get("timezone", "Asia/Kolkata")
        return env

    def get_command(self, d):
        """
        Get the command that must be run
        """

        # To or from cloud
        direction = self.direction

        # Extra params..
        params = self.get_params()

        if "aws" in self.args:
            prefix = "s3"
            bucket = self.args["aws"]["bucket"]
        elif "gcp" in self.args:
            prefix = "gs"
            bucket = self.args["gcp"]["bucket"]
        else:
            raise Exception("Unsupported source/destination")

        # Resolve the source and destination
        if direction == "tocloud":
            src = self.config.get_file(d["src"])
            dst = d["dst"] % params
            dst = "{}://{}/{}".format(prefix, bucket, dst)
        else:
            dst = os.path.abspath(self.config.get_file(d["dst"]))
            src = d["src"] % params
            src = "{}://{}/{}".format(prefix, bucket, src)

        if "aws" in self.args:

            # aws s3 sync s3://mybucket s3://mybucket2
            if direction == "tocloud" and os.path.isfile(src):
                awscmd = ["aws", "s3", "cp", "--quiet"]
            else:
                awscmd = ["aws", "s3", "sync", "--quiet"]

            if self.config.dryrun:
                awscmd.append("--dryrun")

            awscmd.extend([src, dst])
            return awscmd

        if "gcp" in self.args:

            # gsutil sync gs://mybucket gs://mybucket2
            if direction == "tocloud" and os.path.isfile(src):
                gscmd = ["gsutil", "cp"]
            else:
                gscmd = ["gsutil", "-m", "-q", "rsync", "-r"]

            if self.config.dryrun:
                gscmd.append("-n")

            # Add source and destination
            gscmd.extend([src, dst])

            return gscmd

        raise Exception("Unsupported source/destination")

    # => Now run the command
    def run_sync(self, state):
        """
        Run the backup task
        """

        env = self.get_env()

        dirspecs = self.args[self.dirspecs]
        for d in dirspecs:
            enable = d.get("enable", True)
            if not enable:
                continue

            name = d["name"]

            # => What should I be running?
            cmd = self.get_command(d)

            # Now run the command
            p = subprocess.Popen(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = p.communicate()
            out = str(out, "utf-8")
            err = str(err, "utf-8")

            msg = """\
Cmd: {}
Error
-----
{}

Output:
-------
{}"""
            msg = msg.format(" ".join(cmd), err, out)

            # Log cloud-specific information
            if "BOTO_CONFIG" in env:
                msg += "Boto Config: {}".format(env["BOTO_CONFIG"])

            logger.debug(
                "Backing up {}".format(name),
                extra=self.config.get_extra({"transform": self.name, "data": msg}),
            )

        logger.debug(
            "Sync'd all dirs",
            extra=self.config.get_extra(
                {
                    "transform": self.name,
                }
            ),
        )

    def run(self, state):
        return self.run_sync(state)


class BackupCoreTask(CloudMixin, Task):
    """
    Backsup code and data as required
    """

    NAME = "BackupCoreTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "BackupCoreTask"
        self.dirspecs = "backupdirs"
        self.direction = "tocloud"


class SyncLocalCoreTask(CloudMixin, Task):
    """
    Syncs a local directory with  content of a s3 bucket
    """

    NAME = "SyncLocalCoreTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SyncLocalCoreTask"
        self.dirspecs = "localdirs"
        self.direction = "fromcloud"
