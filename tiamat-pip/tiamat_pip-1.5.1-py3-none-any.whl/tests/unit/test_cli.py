import os
from unittest.mock import patch

import tiamatpip.cli
from tiamatpip import configure


def test_should_redirect_argv_empty_args():
    ret = tiamatpip.cli.should_redirect_argv([])
    assert ret is False


def test_should_redirect_argv_tiamat_pip_install_env():
    with patch.dict(os.environ, {"TIAMAT_PIP_INSTALL": "true"}):
        ret = tiamatpip.cli.should_redirect_argv([])
        assert ret is True


def test_should_redirect_argv_match_pip_command_name():
    pip_command_name = configure.get_pip_command_name()
    ret = tiamatpip.cli.should_redirect_argv(["foo", pip_command_name])
    assert ret is True


def test_should_redirect_argv_no_match_pip_command_name():
    pip_command_name = "bar"
    ret = tiamatpip.cli.should_redirect_argv(["foo", pip_command_name])
    assert ret is False
