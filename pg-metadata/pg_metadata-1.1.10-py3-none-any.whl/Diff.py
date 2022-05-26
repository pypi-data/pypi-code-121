#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
from shutil import rmtree

from pg_metadata.Database import Database
from pg_metadata.System   import SEP, SetupLogging

class Diff():
    def __init__(self, config):
        self.ConnectSource = config.get("source") or {}
        self.ConnectTarget = config.get("target") or {}

        self.Path = (config.get("path") or "").strip()
        assert len(self.Path) > 0, \
            "Comparer path is null"

        self.PathSource = "/".join([self.Path, "_source"])
        self.PathTarget = "/".join([self.Path, "_target"])
        self.PathDiff   = "/".join([self.Path, "_diff"])

        self.ExcludeSchemas = config.get("exclude_schemas") or []

        SetupLogging(config)

    def GetPath(self, db, root, object):
        # Get file name and path
        file_name = (object.GetFileName() or "").strip()
        path = object.GetPath() or []

        # File name not found - get from parent object
        if len(file_name) <= 0:
            parent = db.Objects.get(object.Parent)
            file_name = (parent.GetFileName() or "").strip()
            path = parent.GetPath() or []

        assert len(file_name) > 0, \
            "Object file name is null"

        assert len(path) > 0, \
            "Object path is null"

        # Create subfolders
        path = "/".join([root] + path)
        if not os.path.exists(path):
            os.makedirs(path)

        return "/".join([path, file_name])

    def Run(self):
        logging.info("Diff started")

        logging.info("Path = {0}".format(self.Path))
        logging.info("PathSource = {0}".format(self.PathSource))
        logging.info("PathTarget = {0}".format(self.PathTarget))
        logging.info("PathDiff = {0}".format(self.PathDiff))

        # Recreate root folder
        if os.path.exists(self.Path):
            rmtree(self.Path)
        os.mkdir(self.Path)

        # Subfolders
        os.mkdir(self.PathSource)
        os.mkdir(self.PathTarget)
        os.mkdir(self.PathDiff)

        logging.info("Folders created")

        # Parse and export source database
        source_db = Database(self.ConnectSource, self.ExcludeSchemas)
        source_db.Parse()

        logging.info("Source db parsed, {0} objects".format(len(source_db.Objects)))

        # Parse and export target database
        target_db = Database(self.ConnectTarget, self.ExcludeSchemas)
        target_db.Parse()

        logging.info("Target db parsed, {0} objects".format(len(source_db.Objects)))

        # Iterate objects of source database
        for sk, sv in source_db.Objects.items():

            # IN source, NOT IN target
            if sk not in target_db.Objects.keys():

                # Parent isn't in target too
                if len(sv.Parent or "") > 0 and sv.Parent not in target_db.Objects.keys():
                    continue

                logging.debug("CREATE {0} not in target".format(sk))

                # Write CREATE to source
                with open(self.GetPath(source_db, self.PathSource, sv), "a", encoding="utf-8") as wf:
                    wf.write(sv.DDL_Create())
                    wf.write(SEP + SEP)

                # Write CREATE to diff
                with open(self.GetPath(source_db, self.PathDiff, sv), "a", encoding="utf-8") as wf:
                    wf.write(sv.DDL_Create())
                    wf.write(SEP + SEP)

                # Write CREATE to object type file
                with open(sv.GetObjectTypeFile(self.Path), "a", encoding="utf-8") as wf:
                    wf.write(tv.DDL_Create())
                    wf.write(SEP + SEP)

            # IN source, IN target
            else:
                tv = target_db.Objects.get(sk)

                # Calculate diff
                diff = sv.Diff(tv)
                if len(diff or []) <= 0:
                    continue

                logging.debug("DIFF {0} both source and target".format(sk))

                # Write CREATE to source
                with open(self.GetPath(source_db, self.PathSource, sv), "a", encoding="utf-8") as wf:
                    wf.write(sv.DDL_Create())
                    wf.write(SEP + SEP)

                # Write CREATE to target
                with open(self.GetPath(target_db, self.PathTarget, tv), "a", encoding="utf-8") as wf:
                    wf.write(tv.DDL_Create())
                    wf.write(SEP + SEP)

                # Write DROP and CREATE to diff
                with open(self.GetPath(source_db, self.PathDiff, sv), "a", encoding="utf-8") as wf:
                    wf.write((SEP+SEP).join(diff))
                    wf.write(SEP + SEP)

                # Write DROP and CREATE to object type file
                with open(sv.GetObjectTypeFile(self.Path), "a", encoding="utf-8") as wf:
                    wf.write((SEP).join(diff))
                    wf.write(SEP + SEP)

        # Iterate objects of target database
        for tk, tv in target_db.Objects.items():

            # NOT IN source, IN target
            if tk in source_db.Objects.keys():
                continue

            # Parent object deleted in source DB
            if len(tv.Parent or "") > 0 and tv.Parent not in source_db.Objects.keys():
                continue

            logging.debug("DROP {0} not in source".format(sk))

            # Write CREATE to target
            with open(self.GetPath(target_db, self.PathTarget, tv), "a", encoding="utf-8") as wf:
                wf.write(tv.DDL_Create())
                wf.write(SEP + SEP)

            # Write DROP to diff
            with open(self.GetPath(target_db, self.PathDiff, tv), "a", encoding="utf-8") as wf:
                wf.write(tv.DDL_Drop())
                wf.write(SEP + SEP)

            # Write DROP to object type file
            with open(sv.GetObjectTypeFile(self.Path), "a", encoding="utf-8") as wf:
                wf.write(tv.DDL_Drop())
                wf.write(SEP + SEP)
