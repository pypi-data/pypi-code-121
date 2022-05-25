# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxrun.tests import Test


class Command(Test):
    devices = ["qemu-*", "fvp-aemva"]
    name = "command"
    timeout = 2

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("command.yaml.jinja2", **kwargs)
