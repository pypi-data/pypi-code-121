import os

import immutables
import pytest
import yaml
from sym.shared.cli.helpers.contexts import push_env

from ...helpers.config import Config, deepget, store_login_config
from ...models import Organization


@pytest.fixture
def org() -> Organization:
    return Organization(slug="slug", client_id="client-id")


@pytest.fixture
def email() -> str:
    return "ci@symops.io"


__config_yaml = """
auth_token:
  access_token: access
  expires_in: 86400
  refresh_token: refresh
  scope: scopes
  token_type: type
client_id: client-id
email: ci@symops.io
org: slug
"""


def test_write_login_config(sandbox, org, email, auth_token):
    with push_env("XDG_CONFIG_HOME", str(sandbox.path / ".config")):
        path = store_login_config(email=email, org=org, auth_token=auth_token)
        with open(path) as fd:
            data = fd.read()
            assert data.strip() == __config_yaml.strip()


def test_read_login_config(sandbox, org, email, auth_token):
    with push_env("XDG_CONFIG_HOME", str(sandbox.path / ".config")):
        config_dir = sandbox.path / ".config" / "symflow" / "default"
        os.makedirs(config_dir)
        with open(str(config_dir / "config.yml"), "w") as fd:
            fd.write(__config_yaml)
            fd.flush()
            assert Config.get_email() == email
            assert Config.get_org() == immutables.Map(org)
            assert Config.get_access_token() == "access"


def test_logout(sandbox, org, email, auth_token):
    with push_env("XDG_CONFIG_HOME", str(sandbox.path / ".config")):
        path = store_login_config(email=email, org=org, auth_token=auth_token)
        with open(path) as fd:
            data = fd.read()
            assert data.strip() == __config_yaml.strip()

        Config.logout()
        with open(path, "r") as fd:
            data = yaml.safe_load(fd.read())
            assert "email" not in data


def test_config_get_org(org, email, auth_token):
    store_login_config(email=email, org=org, auth_token=auth_token)
    assert Config.get_value("org") == org["slug"]


TEST_DICT = {"first": {"second": {"foo": "bar"}}}


def test_deepget_should_return_none_on_bad_key():
    assert deepget("wrong.bad", TEST_DICT) is None


def test_deepget_should_return_the_correct_value():
    assert deepget("first.second.foo", TEST_DICT) == "bar"
