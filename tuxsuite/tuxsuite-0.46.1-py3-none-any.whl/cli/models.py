# -*- coding: utf-8 -*-

from dataclasses import asdict, dataclass, field, fields
from typing import Dict, List

import json


class Base:
    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())

    @classmethod
    def new(cls, **kwargs):
        fields_names = [f.name for f in fields(cls)]
        i_kwargs = {}
        v_kwargs = {}
        for k in kwargs:
            if k in fields_names:
                v_kwargs[k] = kwargs[k]
            else:
                i_kwargs[k] = kwargs[k]

        return cls(**v_kwargs, extra=i_kwargs)


@dataclass
class Build(Base):
    project: str
    uid: str
    plan: str
    kconfig: List[str]
    target_arch: str
    toolchain: str
    build_name: str
    client_token: str
    environment: Dict
    make_variables: Dict
    targets: List[str]
    git_repo: str
    git_ref: str
    git_sha: str
    download_url: str
    kernel_image: str
    user: str
    state: str
    result: str
    waited_by: List[str]
    errors_count: int
    warnings_count: int
    provisioning_time: str
    running_time: str
    finished_time: str
    extra: Dict
    git_short_log: str = None
    sccache_hits: int = None
    duration: int = None
    build_status: str = None
    sccache_misses: int = None
    tuxbuild_status: str = None
    kernel_version: str = None
    kernel_image_name: str = None
    status_message: str = None
    git_describe: str = None

    def __lt__(self, other):
        return (self.target_arch, self.toolchain) < (other.target_arch, other.toolchain)

    def url(self):
        (grp, prj) = self.project.split("/")
        return f"/v1/groups/{grp}/projects/{prj}/builds/{self.uid}"


@dataclass
class Test(Base):
    project: str
    device: str
    uid: str
    kernel: str
    modules: str
    tests: List[str]
    state: str
    result: str
    results: Dict[str, str]
    plan: str
    waiting_for: str
    provisioning_time: str
    running_time: str
    finished_time: str
    extra: Dict
    duration: int = None
    boot_args: str = None
    user: str = None

    def __lt__(self, other):
        return self.device < other.device

    def url(self):
        (grp, prj) = self.project.split("/")
        return f"/v1/groups/{grp}/projects/{prj}/tests/{self.uid}"

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())


@dataclass
class Plan(Base):
    project: str
    uid: str
    name: str
    description: str
    extra: Dict
    builds: List = field(default_factory=list)
    tests: List = field(default_factory=list)
    provisioning_time: str = None
    user: str = None

    def __post_init__(self):
        if self.builds:
            self.builds = [Build.new(**b) for b in self.builds["results"]]
        if self.tests:
            self.tests = [Test.new(**t) for t in self.tests["results"]]

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())

    def _tests_wait_for(self, uid):
        return [t for t in self.tests if t.waiting_for == uid]

    def filter_builds(self, f):
        return sorted([b for b in self.builds if f(self, b)])

    def filter_tests(self, f):
        return sorted([t for t in self.tests if f(self, t)])

    def passing(self):
        def __filter(plan, build):
            return (build.result == "pass" and build.warnings_count == 0) and (
                all([t.result == "pass" for t in plan._tests_wait_for(build.uid)])
            )

        return self.filter_builds(__filter)

    def warning(self):
        def __filter(plan, build):
            return (build.result == "pass" and build.warnings_count != 0) and (
                all([t.result == "pass" for t in self._tests_wait_for(build.uid)])
            )

        return self.filter_builds(__filter)

    def failing(self):
        def __filter(plan, build):
            return build.result == "fail" or any(
                [t.result == "fail" for t in self._tests_wait_for(build.uid)]
            )

        return self.filter_builds(__filter)

    def errors(self):
        def __filter(plan, build):
            return build.result == "error" or any(
                [t.result == "error" for t in self._tests_wait_for(build.uid)]
            )

        return self.filter_builds(__filter)
