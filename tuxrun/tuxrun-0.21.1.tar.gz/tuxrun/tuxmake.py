# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import contextlib
import json
from pathlib import Path

from tuxrun.requests import requests_get


class InvalidTuxBuild(Exception):
    pass


class TuxBuild:
    Invalid = InvalidTuxBuild

    @classmethod
    def parse(cls, url, data):
        try:
            metadata = json.loads(data)
        except json.JSONDecodeError as e:
            raise cls.Invalid(f"Invalid metadata.json: {e}")

        try:
            target_arch = metadata["build"]["target_arch"]
        except KeyError:
            raise cls.Invalid("{url}/metadata.json is invalid")

        kernel = modules = None
        with contextlib.suppress(KeyError):
            kernel = url + "/" + metadata["results"]["artifacts"]["kernel"][0]
        with contextlib.suppress(IndexError, KeyError):
            modules = url + "/" + metadata["results"]["artifacts"]["modules"][0]

        return (target_arch, kernel, modules)


class TuxBuildBuild(TuxBuild):
    def __init__(self, url):
        self.url = url
        ret = requests_get(f"{url}/metadata.json")
        if ret.status_code != 200:
            raise self.Invalid(f"{url}/metadata.json is missing")

        (self.target_arch, self.kernel, self.modules) = TuxBuild.parse(url, ret.text)


class TuxMakeBuild(TuxBuild):
    def __init__(self, directory):
        self.location = Path(directory).resolve()
        self.url = f"file://{self.location}"
        metadata_file = self.location / "metadata.json"
        if not self.location.is_dir():
            raise self.Invalid(f"{directory} is not a directory")
        if not metadata_file.exists():
            raise self.Invalid(
                f"{directory} is not a valid TuxMake artifacts directory: missing metadata.json"
            )

        (self.target_arch, self.kernel, self.modules) = TuxBuild.parse(
            f"file://{self.location}", metadata_file.read_text(encoding="utf-8")
        )
