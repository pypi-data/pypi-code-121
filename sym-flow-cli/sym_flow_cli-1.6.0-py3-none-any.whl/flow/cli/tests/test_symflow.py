from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.version import __version__


def test_version(click_setup):
    with click_setup() as runner:
        result = runner.invoke(click_command, ["version"])
        assert result.exit_code == 0
        assert result.output == f"{__version__}\n"
