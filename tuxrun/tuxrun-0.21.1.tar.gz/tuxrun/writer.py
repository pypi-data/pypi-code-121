# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from contextlib import ContextDecorator
import logging
import sys
import yaml

from tuxrun.yaml import yaml_load


COLORS = {
    "exception": "\033[1;31m",
    "error": "\033[1;31m",
    "warning": "\033[1;33m",
    "info": "\033[1;37m",
    "debug": "\033[0;37m",
    "target": "\033[32m",
    "input": "\033[0;35m",
    "feedback": "\033[0;33m",
    "results": "\033[1;34m",
    "dt": "\033[0;90m",
    "end": "\033[0m",
}
LOG = logging.getLogger("tuxrun")


class Writer(ContextDecorator):
    def __init__(self, log_file):
        self.file = log_file

    def __enter__(self):
        if self.file is not None:
            self.file = self.file.open("w")
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        if self.file is not None:
            self.file.close()

    def write(self, line):
        line = line.rstrip("\n")
        try:
            data = yaml_load(line)
        except yaml.YAMLError:
            sys.stdout.write(line + "\n")
            return
        if not data or not isinstance(data, dict):
            sys.stdout.write(line + "\n")
            return
        if not set(["dt", "lvl", "msg"]).issubset(data.keys()):
            sys.stdout.write(line + "\n")
            return

        if self.file is not None:
            self.file.write("- " + line + "\n")
        else:
            level = data["lvl"]
            msg = data["msg"]
            ns = " "
            if level == "feedback" and "ns" in data:
                ns = f" <{COLORS['feedback']}{data['ns']}{COLORS['end']}> "
            timestamp = data["dt"].split(".")[0]

            if level == "input" and msg[-1] == "\n":
                msg = msg[0:-1] + "⏎"
            sys.stdout.write(
                f"{COLORS['dt']}{timestamp}{COLORS['end']}{ns}{COLORS[level]}{msg}{COLORS['end']}\n"
            )
