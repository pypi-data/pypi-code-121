"""
`embedops_cli_test`
=======================================================================
Unit tests for the CLI interface for EmbedOps tools
* Author(s): Bailey Steinfadt
"""

import os
import pytest
from click.testing import CliRunner
from embedops_cli import embedops_cli
from tests import BBYML_FILENAME, GLYML_FILENAME
from embedops_cli.eo_types import UnauthorizedUserException

NOT_A_FILENAME = "not_a_file.yaml"
GHYML_TEST_DETECTION_FILENAME = ".github/workflows/test-detection-.github-ci.yml"


@pytest.fixture
def change_test_dir(request):
    """
    A function-level fixture that changes to the test case directory,
    run the test (yield), then change back to the calling directory to
    avoid side-effects.
    """
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


def test_version_command():
    """Learned how to write tests for click by testing build in version command"""
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, ["--version"])
    assert result.exit_code == 0
    assert result.output[:21] == "embedops-cli, version"


def test_help_command():
    """Learned how to write tests for click by testing built in help command"""
    runner = CliRunner()
    h_result = runner.invoke(embedops_cli.embedops_cli, "-h")
    assert h_result.exit_code == 0
    help_result = runner.invoke(embedops_cli.embedops_cli, "--help")
    assert help_result.exit_code == 0
    assert help_result.output == h_result.output
    halp_result = runner.invoke(embedops_cli.embedops_cli, "--halp")
    assert halp_result.exit_code == 0
    assert halp_result.output == h_result.output


def test_jobs_command():
    """Test the top level jobs group"""
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "jobs")
    assert result.exit_code == 0
    result = runner.invoke(
        embedops_cli.embedops_cli, ["jobs", "--filename", "not_a_file.yaml"]
    )
    assert result.exit_code == 2


def test_show_jobs_no_filename():
    """Test the show job list command no filename"""
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, ["jobs", "show"])

    assert result.exit_code == 0


def test_show_jobs_nonexistent_filename():
    """Test the show job list command with a nonexistent file"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.embedops_cli, ["jobs", "--filename", "not_a_file.yaml", "show"]
    )
    assert result.exit_code == 2


def test_show_jobs_not_yaml_filename():
    """Test the show job list command with a non-yaml filename"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.embedops_cli, ["jobs", "--filename", "tests/README.md", "show"]
    )
    assert result.exit_code == 1


def test_show_jobs():
    """Test the show job list command correct syntax"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.embedops_cli,
        ["jobs", "--filename", BBYML_FILENAME, "show"],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        embedops_cli.embedops_cli,
        ["jobs", "--filename", GLYML_FILENAME, "show"],
    )
    assert result.exit_code == 0


def test_run_jobs_no_job_name_or_filename():
    """Test the run job command with no job or filename"""

    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, ["jobs", "run"])
    assert result.exit_code == 2


def test_run_jobs_no_job_name():
    """Test the run job list command with no job name"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.embedops_cli,
        ["jobs", "--filename", BBYML_FILENAME, "run"],
    )
    assert result.exit_code == 2


def test_run_jobs_nonexistent_file():
    """Test the run job command with a nonexistent file"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.embedops_cli,
        ["jobs", "--filename", NOT_A_FILENAME, "run", "build"],
    )
    assert result.exit_code == 2


def test_run_jobs_not_yaml_filename():
    """Test the run job command with a non-yaml filename"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.embedops_cli,
        ["jobs", "--filename", "tests/README.md", "run", "build"],
    )
    assert result.exit_code == 1

def test_stale_token_prompts_login(mocker):
    """Test that a no-longer-valid auth token prompts"""
    token_status = mocker.patch("embedops_cli.embedops_cli.embedops_authorization.check_token")
    token_status.return_value = False


    do_login = mocker.patch("embedops_cli.embedops_cli.embedops_authorization.request_authorization")
    do_login.side_effect = UnauthorizedUserException()
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "login")
    do_login.assert_called()

    assert result.exit_code != 0

    # mock `check user` to return false
    # verify that "do login" is called
    # verify that if "do login" is successful that the return value is 0