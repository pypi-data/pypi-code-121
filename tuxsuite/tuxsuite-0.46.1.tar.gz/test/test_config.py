# -*- coding: utf-8 -*-

import pytest
import tuxsuite.config
import tuxsuite.exceptions


def test_config_FileNotFoundError():
    with pytest.raises(tuxsuite.exceptions.TokenNotFound):
        tuxsuite.config.Config(config_path="/nonexistent")


def test_config_token_from_env(monkeypatch, sample_token, tuxauth):
    """Set TUXSUITE_TOKEN in env and ensure it is used"""
    monkeypatch.setenv("TUXSUITE_TOKEN", sample_token)
    c = tuxsuite.config.Config(config_path="/nonexistent")
    assert c.auth_token == sample_token
    assert c.kbapi_url == "https://api.tuxbuild.com/v1"
    assert c.get_auth_token() == c.auth_token
    assert c.get_kbapi_url() == c.kbapi_url
    assert c.get_tuxsuite_env() == c.tuxsuite_env


def test_config_token_and_url_from_env(monkeypatch, sample_token, sample_url, tuxauth):
    """Set TUXSUITE_TOKEN in env and ensure it is used"""
    monkeypatch.setenv("TUXSUITE_TOKEN", sample_token)
    monkeypatch.setenv("TUXSUITE_URL", sample_url)
    c = tuxsuite.config.Config(config_path="/nonexistent")
    assert c.auth_token == sample_token
    assert c.kbapi_url == sample_url
    assert c.get_auth_token() == c.auth_token
    assert c.get_kbapi_url() == c.kbapi_url
    assert c.get_tuxsuite_env() == c.tuxsuite_env


def test_default_config_file(home, tuxauth):
    (home / ".config" / "tuxsuite").mkdir(parents=True)
    (home / ".config" / "tuxsuite" / "config.ini").write_text("[default]\ntoken=1234")
    c = tuxsuite.config.Config()
    c.get_auth_token() == "1234"


def test_config_file_minimum(tmp_path, sample_token, tuxauth):
    contents = """
[default]
token={}
""".format(
        sample_token
    )
    config_file = tmp_path / "config.ini"
    config_file.write_text(contents)
    c = tuxsuite.config.Config(config_path=config_file)
    assert c.auth_token == sample_token
    assert c.kbapi_url == "https://api.tuxbuild.com/v1"
    assert c.get_auth_token() == c.auth_token
    assert c.get_kbapi_url() == c.kbapi_url
    assert c.get_tuxsuite_env() == c.tuxsuite_env


def test_config_file_no_token(tmp_path, tuxauth):
    contents = """
[default]
"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(contents)
    with pytest.raises(tuxsuite.exceptions.TokenNotFound):
        tuxsuite.config.Config(config_path=config_file)


def test_config_file_section(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text("")
    with pytest.raises(tuxsuite.exceptions.InvalidConfiguration):
        tuxsuite.config.Config(config_path=config_file)


def test_config_file_default(tmp_path, sample_token, sample_url, tuxauth):
    contents = """
[default]
token={}
api_url={}
""".format(
        sample_token, sample_url
    )
    config_file = tmp_path / "config.ini"
    config_file.write_text(contents)
    c = tuxsuite.config.Config(config_path=config_file)
    assert c.auth_token == sample_token
    assert c.kbapi_url == sample_url
    assert c.get_auth_token() == c.auth_token
    assert c.get_kbapi_url() == c.kbapi_url
    assert c.get_tuxsuite_env() == c.tuxsuite_env


def test_config_file_non_default(
    monkeypatch, tuxauth, tmp_path, sample_token, sample_url
):
    contents = """
[default]
token=foo
api_url=bar
[foobar]
token={}
api_url={}
""".format(
        sample_token, sample_url
    )
    monkeypatch.setenv("TUXSUITE_ENV", "foobar")
    config_file = tmp_path / "config.ini"
    config_file.write_text(contents)
    c = tuxsuite.config.Config(config_path=config_file)
    assert c.auth_token == sample_token
    assert c.kbapi_url == sample_url
    assert c.get_auth_token() == c.auth_token
    assert c.get_kbapi_url() == c.kbapi_url
    assert c.get_tuxsuite_env() == c.tuxsuite_env


def test_env_config_mix(monkeypatch, tuxauth, home):
    (home / ".config" / "tuxsuite").mkdir(parents=True)
    (home / ".config" / "tuxsuite" / "config.ini").write_text(
        """[default]
token=1234
api_url=https://kbapi/v1/
tuxapi_url=https://tuxapi/v1/
tuxauth_url=https://tuxauth/v1/
group=grp
project=prj"""
    )

    c = tuxsuite.config.Config()
    assert c.get_auth_token() == "1234"
    assert c.get_kbapi_url() == "https://kbapi/v1"
    assert c.tuxapi_url == "https://tuxapi/v1"
    assert c.tuxauth_url == "https://tuxauth/v1"
    assert c.group == "grp"
    assert c.project == "prj"

    monkeypatch.setenv("TUXSUITE_TOKEN", "mytoken")
    monkeypatch.setenv("TUXSUITE_GROUP", "mygrp")
    c = tuxsuite.config.Config()
    assert c.get_auth_token() == "mytoken"
    assert c.get_kbapi_url() == "https://kbapi/v1"
    assert c.tuxapi_url == "https://tuxapi/v1"
    assert c.tuxauth_url == "https://tuxauth/v1"
    assert c.group == "mygrp"
    assert c.project == "prj"

    monkeypatch.setenv("TUXSUITE_PROJECT", "myprj")
    monkeypatch.setenv("TUXSUITE_URL", "https://beta.api/v1/")
    c = tuxsuite.config.Config()
    assert c.get_auth_token() == "mytoken"
    assert c.get_kbapi_url() == "https://beta.api/v1"
    assert c.tuxapi_url == "https://tuxapi/v1"
    assert c.tuxauth_url == "https://tuxauth/v1"
    assert c.group == "mygrp"
    assert c.project == "myprj"


class TestBackwardsCompatibilityWithTuxBuild:
    @pytest.fixture
    def config_dir(self, home):
        d = home / ".config" / "tuxbuild"
        d.mkdir(parents=True)
        return d

    @pytest.fixture
    def config_file(self, config_dir):
        c = config_dir / "config.ini"
        return c

    def test_support_deprecated_tuxbuild_config(self, config_file, caplog, tuxauth):
        config_file.write_text("[default]\ntoken=1234567890")
        c = tuxsuite.config.Config()
        assert c.auth_token == "1234567890"
        assert "~/.config/tuxbuild/config.ini is deprecated" in caplog.text

    def test_support_deprecated_tuxbuild_builds_yaml(self, config_dir, caplog, tuxauth):
        builds = config_dir / "builds.yaml"
        builds.write_text(
            "sets:\n  - name: basic\n    builds:\n      - {target_arch: arm64, toolchain: gcc-10, kconfig: defconfig}"
        )
        c = tuxsuite.config.BuildSetConfig("basic")
        assert len(c.plan) == 1
        assert "~/.config/tuxbuild/builds.yaml is deprecated" in caplog.text

    def test_TUXBUILD_ENV(self, monkeypatch, config_file, caplog, tuxauth):
        monkeypatch.setenv("TUXBUILD_ENV", "test")
        config_file.write_text("[default]\ntoken=1234567890\n[test]\ntoken=abcdefghi")
        c = tuxsuite.config.Config()
        assert c.get_tuxsuite_env() == "test"
        assert c.auth_token == "abcdefghi"
        assert "TUXBUILD_ENV is deprecated" in caplog.text
