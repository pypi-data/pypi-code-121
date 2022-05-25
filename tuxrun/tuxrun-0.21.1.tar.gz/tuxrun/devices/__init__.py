# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxrun.exceptions import InvalidArgument


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


class Device:
    name: str = ""
    flag_use_pre_run_cmd: bool = False
    flag_cache_rootfs: bool = False

    @classmethod
    def select(cls, name):
        for subclass in subclasses(cls):

            if subclass.name == name:
                return subclass
        raise InvalidArgument(
            f"Unknown device {name}. Available: {', '.join([c.name for c in cls.list()])}"
        )

    @classmethod
    def list(cls):
        return sorted([s for s in subclasses(cls) if s.name], key=lambda d: d.name)

    def validate(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def definition(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def device_dict(self, context):
        raise NotImplementedError()  # pragma: no cover


import tuxrun.devices.fvp  # noqa: E402
import tuxrun.devices.qemu  # noqa: E402,F401
