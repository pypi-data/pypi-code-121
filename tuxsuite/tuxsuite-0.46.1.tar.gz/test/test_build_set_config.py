# -*- coding: utf-8 -*-

import os
import pytest
from tuxsuite.config import BuildSetConfig
from tuxsuite.exceptions import InvalidConfiguration


sample_build_set_config = """
sets:
    -   name: basic
        builds:
            - {target_arch: arm64, toolchain: gcc-9, kconfig: defconfig}
            - {target_arch: x86_64, toolchain: gcc-9, kconfig: defconfig}
    -   name: full
        builds:
            - {target_arch: arm64, toolchain: gcc-9, kconfig: defconfig}
            - {target_arch: x86_64, toolchain: gcc-9, kconfig: defconfig}
            - {target_arch: arm, toolchain: gcc-9, kconfig: defconfig}
            - {target_arch: i386, toolchain: gcc-9, kconfig: defconfig}
            - {target_arch: riscv, toolchain: gcc-9, kconfig: defconfig}
"""


@pytest.fixture
def config(tmp_path):
    c = tmp_path / "buildsets.yml"
    c.write_text(sample_build_set_config)
    return c


def test_basics(config):
    basic = BuildSetConfig("basic", config)
    assert len(basic.plan) == 2


def test_full(config):
    full = BuildSetConfig("full", config)
    assert len(full.plan) == 5


def test_empty_config():
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", "/dev/null")


def test_invalid_yaml(tmp_path):
    invalid_config = tmp_path / "test.yml"
    invalid_config.write_text("foo: bar\n- 1\n- 2\n")
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", invalid_config)


def test_missing_sets_key(tmp_path):
    invalid_config = tmp_path / "test.yml"
    invalid_config.write_text("foo: bar\n")
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", invalid_config)


def test_missing_set(config):
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("unknown-set", config)


def test_missing_builds_key_in_set(tmp_path):
    missing_builds = tmp_path / "sets.yaml"
    missing_builds.write_text("sets:\n  - name: basic")
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", missing_builds)


def test_empty_build_list(tmp_path):
    empty_build_list = tmp_path / "sets.yaml"
    empty_build_list.write_text("sets:\n  - name: basic\n    builds: []\n")
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", empty_build_list)


def test_default_filename(mocker):
    mocker.patch("tuxsuite.config.BuildSetConfig.__load_config__")
    build_set_config = BuildSetConfig("basic")
    assert str(build_set_config.filename) == os.path.expanduser(
        "~/.config/tuxsuite/builds.yaml"
    )


def test_missing_file():
    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", "/path/to/nonexisting/file")


def test_config_url(get, response):
    response._content = bytes(sample_build_set_config, "utf-8")

    build = BuildSetConfig("basic", "http://example.com/builds.yaml")
    assert build.filename == "http://example.com/builds.yaml"
    assert len(build.plan) == 2


def test_config_url_404(get, response):
    response.status_code = 404

    with pytest.raises(InvalidConfiguration):
        BuildSetConfig("basic", "http://example.com/builds.yaml")
