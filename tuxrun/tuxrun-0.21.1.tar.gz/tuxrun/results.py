# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import logging
import re

import yaml

from tuxrun.yaml import yaml_load


LOG = logging.getLogger("tuxrun")
PATTERN = re.compile(r"^(\d+_)")


class Results:
    def __init__(self, tests):
        self.__data__ = {}
        self.__post_processed = False
        self.__tests__ = set(["lava"] + [t.name for t in tests])
        self.__ret__ = 0

    def parse(self, line):
        try:
            data = yaml_load(line)
        except yaml.YAMLError:
            LOG.debug(line)
            return
        if not data or not isinstance(data, dict):
            LOG.debug(line)
            return
        if data.get("lvl") != "results":
            return

        test = data.get("msg")
        if not set(["case", "definition"]).issubset(test.keys()):
            LOG.debug(line)
            return

        definition = re.sub(PATTERN, "", test.pop("definition"))
        case = re.sub(PATTERN, "", test.pop("case"))
        self.__data__.setdefault(definition, {})[case] = test
        if test["result"] == "fail":
            self.__ret__ = 1

    def __post_process(self):
        if self.__post_processed:
            return
        self.__post_processed = True

        if self.__tests__ != set(self.__data__.keys()):
            self.__ret__ = 2

    @property
    def data(self):
        self.__post_process()
        return self.__data__

    def ret(self):
        self.__post_process()
        return self.__ret__
