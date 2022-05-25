import pytest


@pytest.mark.parametrize(
    "command",
    (
        "download",
        "show",
        "check",
        "config",
        "search",
        "cache",
        "wheel",
        "hash",
        "completion",
        "debug"
    )
)
def test_command(project, command):
    """
    Test that we properly handle unsupported tiamat-pip commands.
    """
    ret = project.run("pip", command)
    assert ret.exitcode == 1
