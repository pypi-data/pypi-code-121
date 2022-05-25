# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxrun.tests import Test


class Perf(Test):
    devices = ["qemu-*", "fvp-aemva"]
    name = "perf"
    timeout = 30
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("perf.yaml.jinja2", **kwargs)
