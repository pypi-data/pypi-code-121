import json
import logging
import os
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from tempfile import gettempdir
from unittest import TestCase, mock

import pytest
from jsonschema import ValidationError

from cosapp.core import config
from cosapp.core.config import CoSAppConfiguration

here = os.path.dirname(os.path.abspath(config.__file__))


@pytest.fixture()
def fakeschema():
    with open(os.path.join(here, "configuration_schema.json")) as f:
        schema = f.read()

    class FakeSchema:
        def __init__(self, *args, **kwargs):
            self.f = StringIO(schema)

        def __enter__(self):
            return self.f

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.f.close()

    return FakeSchema


def test_CoSAppConfiguration__init__(fakeschema):
    fake_param_str = json.dumps(
        {"userid": "id1234", "roles": [["scope1", "scope2"], ["scope3", "scope4"]]}
    )
    fake_io = StringIO(fake_param_str)
    with mock.patch("builtins.open") as mock_open:

        def fake_open(file, mode="r", **kwargs):
            if str(file).endswith("configuration_schema.json"):
                return fakeschema()

            if "r" in mode:
                return fake_io
            else:
                return mock.DEFAULT

        mock_open.side_effect = fake_open  # Emulate access to configuration file

        c = CoSAppConfiguration()
        assert c.userid == "id1234"
        assert {"scope1", "scope2"} in c.roles
        assert {"scope3", "scope4"} in c.roles


def test_CoSAppConfiguration_userid():
    c = CoSAppConfiguration()
    with pytest.raises(AttributeError):
        c.userid = "r12345"


def test_CoSAppConfiguration_roles():
    c = CoSAppConfiguration()
    with pytest.raises(AttributeError):
        c.roles = [["r12345"]]


def test_CoSAppConfiguration_validate_file(fakeschema):
    # minimal
    fake_io = StringIO(json.dumps({"userid": "a", "roles": []}))
    with mock.patch("builtins.open") as mock_open:

        def fake_open(file, mode="r", **kwargs):
            if str(file).endswith("configuration_schema.json"):
                return fakeschema()

            if "r" in mode:
                return fake_io
            else:
                return mock.DEFAULT

        mock_open.side_effect = fake_open  # Emulate access to configuration file

        c = CoSAppConfiguration()
        assert c.userid == "a"
        assert len(c.roles) == 0


@pytest.mark.parametrize(
    "configuration",
    [
        ({"userid": "", "roles": [["role1"]]}),  # userid to short
        ({"roles": [["role1"]]}),  # userid missing
        ({"userid": "abc"}),  # roles missing
        ({"userid": "", "roles": [["role1"]], "banana": 42}),  # unexpected keyword
        ({"userid": "", "roles": ["role1"]}),  # role is not an array
        ({"userid": "", "roles": [["role1", 1]]}),  # role contains none string element
        ({"userid": "", "roles": [["role1", "role2"], ["role1", "role2"]]}),  # duplicated role
        ({"userid": "", "roles": [["role1", "role2"], ["role3", "role3"]]}),  # duplicated tag in role
        ({"userid": "", "roles": [["role1", "role2"], ["role3", ""]]}),  # empty tag string
    ],
)
def test_CoSAppConfiguration_validate_file_error(fakeschema, configuration):
    fake_io = StringIO(json.dumps(configuration))
    with mock.patch("builtins.open") as mock_open:

        def fake_open(file, mode="r", **kwargs):
            if str(file).endswith("configuration_schema.json"):
                return fakeschema()

            if "r" in mode:
                return fake_io
            else:
                return mock.DEFAULT

        mock_open.side_effect = fake_open  # Emulate access to configuration file

        with pytest.raises(ValidationError):
            CoSAppConfiguration()


def test_CoSAppConfiguration_update_configuration(fakeschema):
    init = {"userid": "ab123", "roles": [["role1"]]}
    fake_param_str = json.dumps(init)
    fake_io = StringIO(fake_param_str)
    with mock.patch("builtins.open") as mock_open:

        def fake_open(file, mode="r", **kwargs):
            if str(file).endswith("configuration_schema.json"):
                return fakeschema()

            if "r" in mode:
                return fake_io
            else:
                return mock.DEFAULT

        mock_open.side_effect = fake_open  # Emulate access to configuration file

        c = CoSAppConfiguration()  # update_configuration is called during the init
        assert c.userid == "ab123"
        assert mock.call.__enter__().write('["role1"') in mock_open.return_value.mock_calls


def test_CoSAppConfiguration_config_var_env(fakeschema):
    folder = Path(gettempdir()).joinpath("dummy_cosapp")
    os.environ["COSAPP_CONFIG_DIR"] = str(folder)
    init = {"userid": "ab123", "roles": [["role1"]]}
    fake_param_str = json.dumps(init)
    fake_io = StringIO(fake_param_str)
    with mock.patch("builtins.open") as mock_open:

        def fake_open(file, mode="r", **kwargs):
            if str(file).endswith("configuration_schema.json"):
                return fakeschema()

            if "r" in mode:
                return fake_io
            else:
                return mock.DEFAULT

        mock_open.side_effect = fake_open  # Emulate access to configuration file

        CoSAppConfiguration()

        config_file = folder.joinpath(CoSAppConfiguration.CONFIG_FILE)
        for call in mock_open.calls:
            call in [mock.call(config_file, "r"), mock.call(config_file, "w")]


def test_CoSAppConfiguration___init__oserror(caplog):
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        with mock.patch("builtins.open") as mock_open:
            mock_open.side_effect = PermissionError

            CoSAppConfiguration()

    records = caplog.records
    warnings = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert "The configuration file cannot be opened, fall back to default." in warnings


def test_CoSAppConfiguration_update_configuration_oserror(caplog):
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        c = CoSAppConfiguration()

        with mock.patch("builtins.open") as mock_open:
            mock_open.side_effect = PermissionError
            c.update_configuration()

    records = caplog.records
    warnings = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert "Fail to save configuration locally." in warnings

