# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxrun.tests import Test


class LibGPIOd(Test):
    devices = ["qemu-*", "fvp-aemva"]
    name = "libgpiod"
    timeout = 25
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("libgpiod.yaml.jinja2", **kwargs)
