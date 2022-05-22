#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from shutil import rmtree
from multiprocessing import Pool

from pg_metadata.Database import Database
from pg_metadata.System import SetupLogging

class Grabber():
    def __init__(self, config):
        self.Connect = config.get("connect") or {}

        self.Path = (config.get("path") or "").strip()
        assert len(self.Path) > 0, \
            "Grabber path is null"

        self.ExcludeSchemas = config.get("exclude_schemas") or []
        self.Threads = config.get("threads") or 8

        SetupLogging(config)

    def WriteFile(self, file):
        with open(file.get("path"), "w", encoding="utf8") as wf:
            wf.write(file.get("data"))

    def Run(self):
        database = Database(connect=self.Connect, exclude_schemas=self.ExcludeSchemas)
        database.Parse()

        if os.path.exists(self.Path):
            rmtree(self.Path)

        write_data = []
        for k,o in database.Objects.items():
            path = o.GetPath()
            if len(path) <= 0:
                continue

            file_name = o.GetFileName()
            if len(file_name) <= 0:
                continue

            path = [self.Path] + path
            path = "/".join(path)

            if not os.path.exists(path):
                os.makedirs(path)

            write_data.append({
                "path" : "/".join([path, file_name]),
                "data" : o.DDL_Create()
            })

        if (self.Threads or 1) <= 1:
            for file in write_data:
                self.WriteFile(file)
        else:
            with Pool(self.Threads) as pool:
                pool.map(self.WriteFile, write_data)
