"""
File Operations
^^^^^^^^^^^^^^^

"""
import os
import sys
import abc
import shutil
import numpy as np
import pandas as pd
from enrichsdk import Trigger
from datetime import datetime
import logging

logger = logging.getLogger("app")


class FileOperationsBase(Trigger):
    """
    Base class for a FileOperations transform. For now only
    one action is supported 'copy'. More actions will be
    added in future.

    Example::

            {
                "transform": "FileOperations",
                "enable": true,
                "dependencies": {
                   ....
                },
                "args": {
                    "actions": [
                        {
                            "action": "copy",
                            "src": "%(output)s/%(runid)s/profile.sqlite",
                            "dst": "%(data_root)s/shared/campaigns/profile_daily/profile.sqlite",
                            "backupsuffix": ".backup"
                        },
                     ]
                }
            }

    """

    @classmethod
    def instantiable(cls):
        return False

    def __init__(self, *args, **kwargs):
        super(FileOperationsBase, self).__init__(*args, **kwargs)
        self.name = "FileOperationsBase"
        self.outputs = {}
        self.dependencies = {}

    def preload_clean_args(self, args):
        """
        Clean when the spec is loaded...
        """

        # Update the args
        args = super().preload_clean_args(args)

        # Sanity check...
        if not isinstance(args, dict):
            raise Exception("args should be a dictionary")

        if ("actions" not in args) or (not isinstance(args["actions"], list)):
            raise Exception("actions is missing or invalid")

        for a in args["actions"]:
            if not isinstance(a, dict):
                raise Exception("Each action spec should be a dictionary")
            supported = ["copy"]
            if a["action"] not in supported:
                raise Exception("Unsupported action")

            if a["action"] == "copy":
                if ("src" not in a) or ("dst" not in a):
                    raise Exception(
                        "Each copy action spec should specify a src and dst"
                    )

        return args

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "{} - process".format(self.name),
            extra=self.config.get_extra({"transform": self.name}),
        )

        msg = ""
        actions = self.args["actions"]
        for a in actions:
            action = a["action"]

            # Pass any global variables...
            srcbase = self.config.get_file(a["src"], extra=self.args)
            dstbase = self.config.get_file(a["dst"], extra=self.args)

            if "files" not in a:
                copyactions = [{"src": srcbase, "dst": dstbase}]
            else:
                copyactions = []
                for f in a["files"]:
                    copyactions.append(
                        {
                            "src": os.path.join(srcbase, f),
                            "dst": os.path.join(dstbase, f),
                        }
                    )

            backupsuffix = a.get("backupsuffix", ".backup")
            data_root = self.config.get_file("%(enrich_data_dir)s")
            for ca in copyactions:
                src = ca["src"]
                dst = ca["dst"]

                if not os.path.exists(src):
                    raise Exception("Could not find source: {}".format(src))

                if os.path.exists(dst):
                    backupsuffix = datetime.now().strftime(backupsuffix)
                    backupdst = dst + backupsuffix
                    if os.path.exists(backupdst):
                        if os.path.isdir(backupdst):
                            shutil.rmtree(backupdst)
                        else:
                            os.remove(backupdst)
                    os.rename(dst, dst + backupsuffix)

                try:
                    os.makedirs(os.path.dirname(dst))
                except:
                    pass

                # Handle the directory names
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy(src, dst)

                msg += "Copy: {} => {}\n".format(
                    os.path.relpath(src, data_root), os.path.relpath(dst, data_root)
                )

        logger.debug(
            "{} - Completed".format(self.name),
            extra=self.config.get_extra({"transform": self.name, "data": msg}),
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


provider = FileOperationsBase
