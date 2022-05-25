import os
from unittest.mock import patch


def test_raw_python(project, subtests):
    with subtests.test("exitcode with no exception"):
        # Some pip calls shell out to python with -c or python foo.py; verify
        # that when -c is used, it doesn't continue back in to user code.
        with patch.dict(os.environ, {"TIAMAT_PIP_INSTALL": "1"}):
            ret = project.run("-c", "print('-c SENTINEL')")
            assert ret.exitcode == 0
            assert "-c SENTINEL" in ret.stdout
            assert (
                "No command" not in ret.stdout
            ), '`binary -c "..."` should terminate execution'

    with subtests.test("exitcode with exception"):
        # If -c code raises an exception, we should see the exception and an error code.
        with patch.dict(os.environ, {"TIAMAT_PIP_INSTALL": "1"}):
            ret = project.run("-c", "raise Exception()")
            assert ret.exitcode == 1
            assert "Traceback (most recent call last)" in ret.stderr
            assert (
                "No command" not in ret.stdout
            ), '`binary -c "..."` should terminate execution'
