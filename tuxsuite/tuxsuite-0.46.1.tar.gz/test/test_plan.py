# -*- coding: utf-8 -*-

import pytest

from tuxsuite.config import PlanConfig
import tuxsuite.build
from tuxsuite.exceptions import InvalidConfiguration
from tuxsuite import Plan


def test_plan_config(plan_config):
    cfg = PlanConfig("", "", plan_config)
    assert cfg.name == "Simple plan"
    assert cfg.description == "A simple plan"

    cfg = PlanConfig("hello", "world", plan_config)
    assert cfg.name == "hello"
    assert cfg.description == "world"

    assert len(cfg.plan) == 12
    assert cfg.plan[0]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-8",
    }
    assert cfg.plan[0]["tests"] == [
        {
            "device": "qemu-i386",
            "tests": ["ltp-smoke"],
            "rootfs": "https://example.com/rootfs.ext4.zst",
        }
    ]

    assert cfg.plan[1]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-8",
    }
    assert cfg.plan[1]["tests"] == [{"device": "qemu-i386", "tests": ["ltp-smoke"]}]

    assert cfg.plan[2]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-9",
    }
    assert cfg.plan[2]["tests"] == [{"device": "qemu-i386", "tests": ["ltp-smoke"]}]

    assert cfg.plan[3]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-10",
    }
    assert cfg.plan[3]["tests"] == [{"device": "qemu-i386", "tests": ["ltp-smoke"]}]

    assert cfg.plan[4]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "clang-10",
    }
    assert cfg.plan[4]["tests"] == [{"device": "qemu-i386"}]

    assert cfg.plan[5]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "clang-11",
    }
    assert cfg.plan[5]["tests"] == [{"device": "qemu-i386"}]

    assert cfg.plan[6]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "clang-nightly",
    }
    assert cfg.plan[6]["tests"] == [{"device": "qemu-i386"}]

    assert cfg.plan[7]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "clang-nightly",
    }
    assert cfg.plan[7]["tests"] == [
        {"device": "qemu-i386"},
        {"device": "qemu-i386", "tests": ["ltp-smoke"]},
    ]

    assert cfg.plan[8]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-8",
    }
    assert cfg.plan[8]["tests"] == [
        {"device": "qemu-i386"},
        {"device": "qemu-i386", "tests": ["ltp-smoke"]},
    ]

    assert cfg.plan[9]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-9",
    }
    assert cfg.plan[9]["tests"] == [
        {"device": "qemu-i386"},
        {"device": "qemu-i386", "tests": ["ltp-smoke"]},
    ]

    assert cfg.plan[10]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-10",
    }
    assert cfg.plan[10]["tests"] == [
        {"device": "qemu-i386"},
        {"device": "qemu-i386", "tests": ["ltp-smoke"]},
    ]

    assert cfg.plan[11]["build"] is None
    assert cfg.plan[11]["tests"] == [
        {
            "kernel": "https://storage.tuxboot.com/arm64/Image",
            "device": "qemu-arm64",
            "tests": ["ltp-smoke"],
        },
        {
            "kernel": "https://storage.tuxboot.com/i386/bzImage",
            "device": "qemu-i386",
            "tests": ["ltp-smoke"],
        },
        {
            "kernel": "https://storage.tuxboot.com/mips64/vmlinux",
            "device": "qemu-mips64",
            "tests": ["ltp-smoke"],
        },
        {
            "kernel": "https://storage.tuxboot.com/ppc64/vmlinux",
            "device": "qemu-ppc64",
            "tests": ["ltp-smoke"],
        },
        {
            "kernel": "https://storage.tuxboot.com/riscv64/Image",
            "device": "qemu-riscv64",
            "tests": ["ltp-smoke"],
        },
        {
            "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
            "device": "qemu-x86_64",
            "tests": ["ltp-smoke"],
        },
    ]


def test_bake_plan_config(bake_plan_config):
    cfg = PlanConfig("", "", bake_plan_config)
    assert cfg.name == "armv7 validation"
    assert cfg.description == "Build and test linux kernel for armv7"

    cfg = PlanConfig("hello", "world", bake_plan_config)
    assert cfg.name == "hello"
    assert cfg.description == "world"

    assert len(cfg.plan) == 3


def test_plan_config_job_name(plan_config):
    cfg = PlanConfig("hello", "world", plan_config, "gcc-simple")
    assert len(cfg.plan) == 0

    cfg = PlanConfig("hello", "world", plan_config, "simple-gcc")
    assert len(cfg.plan) == 1
    assert cfg.plan[0]["build"] == {
        "kconfig": "tinyconfig",
        "target_arch": "i386",
        "toolchain": "gcc-8",
    }


def test_bake_plan_config_job_name(bake_plan_config):
    cfg = PlanConfig("hello", "world", bake_plan_config)
    assert len(cfg.plan) == 3

    cfg = PlanConfig("hello", "world", bake_plan_config, "armv7")
    assert len(cfg.plan) == 1
    assert cfg.plan[0]["build"]["machine"] == "ledge-multi-armv7"
    assert not cfg.plan[0]["tests"]


def test_plan_config_version(plan_config_unknown_version):
    with pytest.raises(InvalidConfiguration):
        PlanConfig("hello", "world", plan_config_unknown_version, "gcc-simple")


def test_submit(config, plan_config, mocker):
    cfg = PlanConfig("", "", plan_config)
    plan = Plan(
        cfg,
        git_repo="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        git_ref="master",
        group="tuxgrp",
        project="tuxprj",
        no_cache=True,
    )

    def post(url, headers, data):
        assert "Authorization" in headers
        if url == "https://tuxapi.tuxsuite.com/v1/groups/tuxgrp/projects/tuxprj/plans":
            assert data == {"description": "A simple plan", "name": "Simple plan"}
            return {"uid": "my-plan-uid"}
        if url == "https://tuxapi.tuxsuite.com/v1/groups/tuxgrp/projects/tuxprj/builds":
            assert isinstance(data, dict)
            assert len(data["builds"]) == 11
            builds = data["builds"]
            index = 0
            for p, d in zip(cfg.plan, builds):
                assert p["build"]["toolchain"] == d["toolchain"]
                assert p["build"]["target_arch"] == d["target_arch"]
                assert [p["build"]["kconfig"]] == d["kconfig"]
                assert d["git_ref"] == "master"
                assert (
                    d["git_repo"]
                    == "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
                )
                assert d["plan"] == "my-plan-uid"
                d["uid"] = f"my-build-{index:02}"
                d["download_url"] = f"http://url/{d['uid']}"
                index += 1
            return builds
        if url == "https://tuxapi.tuxsuite.com/v1/groups/tuxgrp/projects/tuxprj/tests":
            assert isinstance(data, list)
            assert len(data) == 21

            tests = []
            for p in cfg.plan:
                tests.extend(p["tests"])

            for t, d in zip(tests, data):
                assert t["device"] == d["device"]
                assert t.get("kernel") == d.get("kernel")
                assert t.get("tests") == d.get("tests")
                assert t.get("rootfs") == d.get("rootfs")

            assert data[0]["waiting_for"] == "my-build-00"
            assert data[1]["waiting_for"] == "my-build-01"
            assert data[2]["waiting_for"] == "my-build-02"
            assert data[3]["waiting_for"] == "my-build-03"
            assert data[4]["waiting_for"] == "my-build-04"
            assert data[5]["waiting_for"] == "my-build-05"
            assert data[6]["waiting_for"] == "my-build-06"
            assert data[7]["waiting_for"] == "my-build-07"
            assert data[8]["waiting_for"] == "my-build-07"
            assert data[9]["waiting_for"] == "my-build-08"
            assert data[10]["waiting_for"] == "my-build-08"
            assert data[11]["waiting_for"] == "my-build-09"
            assert data[12]["waiting_for"] == "my-build-09"
            assert data[13]["waiting_for"] == "my-build-10"
            assert data[14]["waiting_for"] == "my-build-10"
            for i in range(15, 21):
                assert "waiting_for" not in data[i]
                assert "kernel" in data[i]

            for i, d in enumerate(data):
                d["uid"] = f"my-test-{i:02}"
            return data

        assert 0

    mocker.patch("tuxsuite.build.post_request", post)
    plan.submit()

    assert len(plan.builds) == 11
    assert len(plan.tests) == 21


def test_bake_submit(config, bake_plan_config, mocker):
    cfg = PlanConfig("", "", bake_plan_config)
    plan = Plan(
        cfg,
        group="bake_tuxgrp",
        project="bake_tuxprj",
    )

    def post(url, headers, data):
        assert "Authorization" in headers
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/bake_tuxgrp/projects/bake_tuxprj/plans"
        ):
            assert data == {
                "name": "armv7 validation",
                "description": "Build and test linux kernel for armv7",
            }
            return {"uid": "my-plan-uid"}
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/bake_tuxgrp/projects/bake_tuxprj/oebuilds"
        ):
            assert isinstance(data, dict)
            assert len(data["oebuilds"]) == 3
            builds = data["oebuilds"]
            index = 0
            for p, d in zip(cfg.plan, builds):
                assert p["build"]["container"] == d["container"]
                assert p["build"]["distro"] == d["distro"]
                assert p["build"]["envsetup"] == d["envsetup"]
                assert p["build"]["machine"] == d["machine"]
                assert p["build"]["sources"] == d["sources"]
                assert p["build"]["target"] == d["target"]
                assert d["plan"] == "my-plan-uid"
                d["uid"] = f"my-build-{index:02}"
                d["download_url"] = f"http://url/{d['uid']}"
                index += 1
            return builds

        assert 0

    mocker.patch("tuxsuite.build.post_request", post)
    plan.submit()
    assert len(plan.builds) == 3
    assert len(plan.tests) == 0


def test_get_plan(config, plan_config, mocker):
    cfg = PlanConfig("", "", plan_config)
    plan = Plan(
        cfg,
        git_repo="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        git_ref="master",
        group="tuxgrp",
        project="tuxprj",
    )

    calls = 0

    def get(url, headers, params):
        nonlocal calls
        assert "Authorization" in headers
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/tuxgrp/projects/tuxprj/plans/my-1-plan-uid"
        ):
            assert params == {
                "start_builds": None,
                "start_tests": None,
                "start_oebuilds": None,
            }
            return {
                "builds": {"next": None, "results": [], "count": 0},
                "tests": {"next": None, "results": [], "count": 0},
                "oebuilds": {"next": None, "results": [], "count": 0},
            }
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/tuxgrp/projects/tuxprj/plans/my-2-plan-uid"
        ):
            calls += 1
            if calls == 1:
                assert params == {
                    "start_builds": None,
                    "start_tests": None,
                    "start_oebuilds": None,
                }
                return {
                    "builds": {
                        "next": "next_build",
                        "results": [{"uid": "1"}],
                        "count": 1,
                    },
                    "tests": {
                        "next": "next_test",
                        "results": [{"uid": "1"}],
                        "count": 1,
                    },
                    "oebuilds": {
                        "next": None,
                        "results": [],
                        "count": 0,
                    },
                }
            if calls == 2:
                assert params == {
                    "start_builds": "next_build",
                    "start_tests": "next_test",
                    "start_oebuilds": None,
                }
                return {
                    "builds": {
                        "next": "next_build_bis",
                        "results": [{"uid": "2"}],
                        "count": 1,
                    },
                    "tests": {"next": None, "results": [{"uid": "2"}], "count": 1},
                }
            if calls == 3:
                assert params == {
                    "start_builds": "next_build_bis",
                    "start_tests": None,
                    "start_oebuilds": None,
                }
                return {
                    "builds": {"next": None, "results": [{"uid": "3"}], "count": 1},
                    "tests": {"next": None, "results": [{"uid": "3"}], "count": 1},
                }
        assert 0

    plan.plan = "my-1-plan-uid"
    mocker.patch("tuxsuite.build.get_request", get)
    assert plan.get_plan() == {"builds": {}, "tests": {}}

    plan.plan = "my-2-plan-uid"
    mocker.patch("tuxsuite.build.get_request", get)
    assert plan.get_plan() == {
        "builds": {"1": {"uid": "1"}, "2": {"uid": "2"}, "3": {"uid": "3"}},
        "tests": {"1": {"uid": "1"}, "2": {"uid": "2"}},
    }


def test_bake_get_plan(config, mocker, bake_plan_config):
    cfg = PlanConfig("", "", bake_plan_config)
    plan = Plan(
        cfg,
        group="bake_tuxgrp",
        project="bake_tuxprj",
    )

    calls = 0

    def get(url, headers, params):
        nonlocal calls
        assert "Authorization" in headers
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/bake_tuxgrp/projects/bake_tuxprj/plans/my-1-bake_plan-uid"
        ):
            assert params == {
                "start_builds": None,
                "start_tests": None,
                "start_oebuilds": None,
            }
            return {
                "builds": {"next": None, "results": [], "count": 0},
                "tests": {"next": None, "results": [], "count": 0},
                "oebuilds": {"next": None, "results": [], "count": 0},
            }
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/bake_tuxgrp/projects/bake_tuxprj/plans/my-2-bake_plan-uid"
        ):
            calls += 1
            if calls == 1:
                assert params == {
                    "start_builds": None,
                    "start_tests": None,
                    "start_oebuilds": None,
                }
                return {
                    "builds": {
                        "next": None,
                        "results": [],
                        "count": 0,
                    },
                    "tests": {
                        "next": "next_test",
                        "results": [{"uid": "1"}],
                        "count": 1,
                    },
                    "oebuilds": {
                        "next": "next_oebuild",
                        "results": [{"uid": "1"}],
                        "count": 1,
                    },
                }
            if calls == 2:
                assert params == {
                    "start_builds": None,
                    "start_tests": "next_test",
                    "start_oebuilds": "next_oebuild",
                }
                return {
                    "oebuilds": {
                        "next": "next_oebuild_bis",
                        "results": [{"uid": "2"}],
                        "count": 1,
                    },
                    "tests": {"next": None, "results": [{"uid": "2"}], "count": 1},
                }
            if calls == 3:
                assert params == {
                    "start_builds": None,
                    "start_tests": None,
                    "start_oebuilds": "next_oebuild_bis",
                }
                return {
                    "oebuilds": {"next": None, "results": [{"uid": "3"}], "count": 1},
                    "tests": {"next": None, "results": [{"uid": "3"}], "count": 1},
                }
        assert 0

    plan.plan = "my-1-bake_plan-uid"
    mocker.patch("tuxsuite.build.get_request", get)
    assert plan.get_plan() == {"tests": {}, "builds": {}}

    plan.plan = "my-2-bake_plan-uid"
    mocker.patch("tuxsuite.build.get_request", get)
    assert plan.get_plan() == {
        "builds": {"1": {"uid": "1"}, "2": {"uid": "2"}, "3": {"uid": "3"}},
        "tests": {"1": {"uid": "1"}, "2": {"uid": "2"}},
    }


def test_watch(config, mocker, plan_config):
    mocker.patch("time.sleep")
    build_attrs = {
        "group": "tuxgrp",
        "project": "tuxprj",
        "git_repo": "http://github.com/torvalds/linux",
        "git_ref": "master",
        "target_arch": "arm",
        "kconfig": "defconfig",
        "build_name": "test_build_name",
        "toolchain": "gcc-9",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
        "kernel_image": "Image",
    }
    test_attrs = {
        "group": "tuxgrp",
        "project": "tuxprj",
        "token": "test_token",
        "tuxapi_url": "http://tuxapi",
        "kbapi_url": "http://test/foo",
        "device": "qemu-armv7",
        "kernel": "",
    }

    cfg = PlanConfig("", "", plan_config)
    plan = Plan(
        cfg,
        git_repo="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        git_ref="master",
        group="tuxgrp",
        project="tuxprj",
    )

    plan.builds = [
        tuxsuite.build.Build(**build_attrs, uid="build-1"),
        tuxsuite.build.Build(**build_attrs, uid="build-2"),
        tuxsuite.build.Build(**build_attrs, uid="build-3"),
        tuxsuite.build.Build(**build_attrs, uid="build-4"),
    ]
    plan.tests = [
        tuxsuite.build.Test(**test_attrs, uid="test-1"),
        tuxsuite.build.Test(**test_attrs, uid="test-2"),
        tuxsuite.build.Test(**test_attrs, uid="test-3"),
        tuxsuite.build.Test(**test_attrs, uid="test-4"),
    ]

    count = 0

    def get_plan():
        nonlocal count
        count += 1
        if count == 1:
            return {
                "builds": {
                    "build-1": {"state": "queue", "result": "unknown"},
                    "build-2": {"state": "provisioning", "result": "unknown"},
                    "build-3": {"state": "running", "result": "unknown"},
                    "build-4": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                },
                "tests": {
                    "test-1": {"state": "waiting", "result": "unknown"},
                    "test-2": {"state": "provisioning", "result": "unknown"},
                    "test-3": {"state": "running", "result": "unknown"},
                    "test-4": {"state": "finished", "result": "pass"},
                },
            }
        if count == 2:
            return {
                "builds": {
                    "build-1": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                    "build-2": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                    "build-3": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                    "build-4": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                },
                "tests": {
                    "test-1": {"state": "finished", "result": "pass"},
                    "test-2": {"state": "finished", "result": "pass"},
                    "test-3": {"state": "finished", "result": "pass"},
                    "test-4": {"state": "finished", "result": "pass"},
                },
            }
        assert 0

    plan.get_plan = get_plan
    states = list(plan.watch())
    assert len(states) == 14
    assert states[0].build.uid == "build-1"
    assert states[0].state == "queue"
    assert states[1].build.uid == "build-2"
    assert states[1].state == "provisioning"
    assert states[2].build.uid == "build-3"
    assert states[2].state == "running"
    assert states[3].build.uid == "build-4"
    assert states[3].state == "pass"
    assert states[4].build.uid == "test-1"
    assert states[4].state == "waiting"
    assert states[5].build.uid == "test-2"
    assert states[5].state == "provisioning"
    assert states[6].build.uid == "test-3"
    assert states[6].state == "running"
    assert states[7].build.uid == "test-4"
    assert states[7].state == "finished"

    assert states[8].build.uid == "build-1"
    assert states[8].state == "pass"
    assert states[9].build.uid == "build-2"
    assert states[9].state == "pass"
    assert states[10].build.uid == "build-3"
    assert states[10].state == "pass"
    assert states[11].build.uid == "test-1"
    assert states[11].state == "finished"
    assert states[12].build.uid == "test-2"
    assert states[12].state == "finished"
    assert states[13].build.uid == "test-3"
    assert states[13].state == "finished"


def test_bake_watch(config, mocker, bake_plan_config):
    mocker.patch("time.sleep")
    # bake plan watch
    build_attrs = {
        "group": "bake_tuxgrp",
        "project": "bake_tuxprj",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
    }

    cfg = PlanConfig("", "", bake_plan_config)
    plan = Plan(
        cfg,
        group="bake_tuxgrp",
        project="bake_tuxprj",
    )
    plan.builds = []
    uid = 1
    for cfg in cfg.plan:
        if cfg["build"]:
            build_attrs["data"] = cfg["build"]
            plan.builds.append(
                tuxsuite.build.Bitbake(**build_attrs, uid=f"bake_build-{uid}")
            )
            uid += 1

    count = 0

    def get_bake_plan():
        nonlocal count
        count += 1
        if count == 1:
            return {
                "builds": {
                    "bake_build-1": {"state": "provisioning", "result": "unknown"},
                    "bake_build-2": {"state": "running", "result": "unknown"},
                    "bake_build-3": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                },
                "tests": [],
            }
        if count == 2:
            return {
                "builds": {
                    "bake_build-1": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                    "bake_build-2": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                    "bake_build-3": {
                        "state": "finished",
                        "result": "pass",
                        "tuxbuild_status": "pass",
                        "build_status": "pass",
                        "warnings_count": 0,
                    },
                },
                "tests": [],
            }
        assert 0

    plan.get_plan = get_bake_plan
    states = list(plan.watch())
    assert len(states) == 5

    assert states[0].build.uid == "bake_build-1"
    assert states[0].state == "provisioning"
    assert states[1].build.uid == "bake_build-2"
    assert states[1].state == "running"
    assert states[2].build.uid == "bake_build-3"
    assert states[2].state == "finished"

    assert states[3].build.uid == "bake_build-1"
    assert states[3].state == "finished"
    assert states[4].build.uid == "bake_build-2"
    assert states[4].state == "finished"


def test_config_url(get, response, sample_plan_config):
    response._content = bytes(sample_plan_config, "utf-8")

    cfg = PlanConfig("hello", "world", "http://example.com/plan.yaml")
    assert len(cfg.plan) == 12


def test_bake_config_url(get, response, sample_bake_plan_config):
    response._content = bytes(sample_bake_plan_config, "utf-8")

    cfg = PlanConfig("hello", "world", "http://example.com/plan.yaml")
    assert len(cfg.plan) == 3

    with pytest.raises(InvalidConfiguration):
        cfg = PlanConfig("hello", "world", "test/alok")


def test_fetch_errors(get, response):
    response.status_code = 404
    with pytest.raises(InvalidConfiguration):
        PlanConfig("hello", "world", "http://example.com/plan.yaml")
    with pytest.raises(InvalidConfiguration):
        PlanConfig("hello", "world", "/dev/null")
