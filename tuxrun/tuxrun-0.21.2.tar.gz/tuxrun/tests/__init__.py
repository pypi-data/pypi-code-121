# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import fnmatch
from typing import List

from tuxrun import templates
from tuxrun.exceptions import InvalidArgument


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


class Test:
    devices: List[str] = []
    name: str = ""
    timeout: int = 0
    need_test_definition: bool = False

    def __init__(self, timeout):
        if timeout:
            self.timeout = timeout

    @classmethod
    def select(cls, name):
        for subclass in subclasses(cls):

            if subclass.name == name:
                return subclass
        raise InvalidArgument(f"Unknown test {name}")

    @classmethod
    def list(cls, device=None):
        if device is None:
            return sorted(s.name for s in subclasses(cls) if s.name)
        return sorted(
            t.name
            for t in subclasses(cls)
            if t.name and any([fnmatch.fnmatch(device, pat) for pat in t.devices])
        )

    def validate(self, device, **kwargs):
        if not any([fnmatch.fnmatch(device.name, pat) for pat in self.devices]):
            raise InvalidArgument(
                f"Test '{self.name}' not supported on device '{device.name}'"
            )

    def _render(self, filename, **kwargs):
        return templates.tests().get_template(filename).render(**kwargs)


import tuxrun.tests.command  # noqa: E402
import tuxrun.tests.kselftest  # noqa: E402
import tuxrun.tests.kunit  # noqa: E402
import tuxrun.tests.libgpiod  # noqa: E402
import tuxrun.tests.libhugetlbfs  # noqa: E402
import tuxrun.tests.ltp  # noqa: E402
import tuxrun.tests.morello  # noqa: E402,F401
import tuxrun.tests.perf  # noqa: E402,F401
import tuxrun.tests.rcutorture  # noqa: E402,F401
import tuxrun.tests.v4l2  # noqa: E402,F401
