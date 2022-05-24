# -*- coding: utf-8 -*-

import pytest
import tuxsuite


@pytest.fixture(autouse=True)
def reset_config():
    tuxsuite.__config__ = None


@pytest.fixture
def params():
    return {
        "git_repo": "https://github.com/torvalds/linux.git",
        "git_ref": "master",
        "target_arch": "arm64",
        "toolchain": "gcc-9",
        "kconfig": ["defconfig"],
    }


def test_new_build(config, params):
    build = tuxsuite.Build(**params)
    assert build.token is not None
    assert build.kbapi_url is not None
