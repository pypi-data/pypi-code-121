"""
`create_run_test.py`
=======================================================================
Unit tests for code to create CI run records based on CI environment variables
* Author(s): Bryan Siepert
"""
from uuid import uuid1
import pytest
from unittest.mock import MagicMixin, MagicMock, call
from embedops_cli.eotools.ci_run import CIRun, create_entry

from embedops_cli.api.models import CIRun as APICIRun
from embedops_cli.api import rest

"""
- Given an
    - analysis type
    - commit sha
    - branch name
    - embedops api key
    - embedops host
- Then
    - The commit sha, branch name, and analysis type should be set as parameters to the CI run creation API call
    - An API Call should be made to the CI run creation endpoint on the given host
- Given
    - An API response with a 2xx return code
- Then
    - The included record id should be printed to stdout
    - The return code should be 0
"""


class TestEntrypoint:
    @pytest.fixture(autouse=True)
    def configure_env(self, monkeypatch, mocker):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("EMBEDOPS_API_REPO_KEY", "special_pwefix")
        monkeypatch.setenv("EMBEDOPS_ANALYSIS_TYPE", "memusage")
        monkeypatch.setenv("BITBUCKET_BRANCH", "main")
        monkeypatch.setenv("BITBUCKET_BUILD_NUMBER", "10")
        monkeypatch.setenv("BITBUCKET_COMMIT", "abcd1234")
        monkeypatch.setenv(
            "BITBUCKET_GIT_HTTP_ORIGIN", "http://bitbucket.org/dojofive/embedops-tools"
        )
        monkeypatch.setenv("BITBUCKET_STEP_UUID", "yoo-yoo-eye-dee")
        self.ci_run_caller = mocker.patch(
            "embedops_cli.eotools.create_run.CIRun.create"
        )
        self.logger_mock = mocker.patch("embedops_cli.eotools.ci_run._logger")
        self.ci_run = CIRun()
        yield
        del self.ci_run

    def test_ci_envvar_not_set_is_local(self, monkeypatch):
        """If we're not in CI we shant create a CI run, return zero, and output "LOCAL" for the id"""

        monkeypatch.delenv("CI")

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create_entry()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        self.logger_mock.info.assert_called_with("LOCAL")
        self.ci_run_caller.assert_not_called()

    def test_no_commit_id(self, monkeypatch):
        if getenv("BITBUCKET_COMMIT"):
            monkeypatch.delenv("BITBUCKET_COMMIT")
        if getenv("GITHUB_SHA"):
            monkeypatch.delenv("GITHUB_SHA")
        if getenv("CI_COMMIT_SHA"):
            monkeypatch.delenv("CI_COMMIT_SHA")
        ci_run = CIRun()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            ci_run.create_main()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

        self.logger_mock.error.has_calls(call("ERROR: No commit id envvar found"))
        self.ci_run_caller.assert_not_called()

    def test_no_branch_name(self, monkeypatch):
        monkeypatch.delenv("BITBUCKET_BRANCH")
        ci_run = CIRun()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            ci_run.create_main()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

        self.logger_mock.error.assert_has_calls(
            [call("ERROR: No branch name envvar found")]
        )
        self.ci_run_caller.assert_not_called()

    def test_no_analysis_type(self, monkeypatch):
        monkeypatch.delenv("EMBEDOPS_ANALYSIS_TYPE")
        ci_run = CIRun()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            ci_run.create_main()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

        self.logger_mock.error.assert_has_calls(
            [call("ERROR: No analysis type envvar found")]
        )
        self.ci_run_caller.assert_not_called()

    def test_multiple_errors_shown(self, monkeypatch):

        monkeypatch.delenv("EMBEDOPS_ANALYSIS_TYPE", "memusage")
        # remove commit envvars
        if getenv("BITBUCKET_COMMIT"):
            monkeypatch.delenv("BITBUCKET_COMMIT")
        if getenv("GITHUB_SHA"):
            monkeypatch.delenv("GITHUB_SHA")
        if getenv("CI_COMMIT_SHA"):
            monkeypatch.delenv("CI_COMMIT_SHA")

        # remove branch envvars
        if getenv("BITBUCKET_BRANCH"):
            monkeypatch.delenv("BITBUCKET_BRANCH")
        if getenv("GITHUB_REF_NAME"):
            monkeypatch.delenv("GITHUB_REF_NAME")
        if getenv("CI_COMMIT_REF_NAME"):
            monkeypatch.delenv("CI_COMMIT_REF_NAME")

        ci_run = CIRun()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            ci_run.create_main()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

        expected_calls = [
            call("ERROR: No analysis type envvar found"),
            call("ERROR: No branch name envvar found"),
            call("ERROR: No commit id envvar found"),
        ]

        self.logger_mock.error.assert_has_calls(expected_calls, any_order=True)
        self.ci_run_caller.assert_not_called()

    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("EMBEDOPS_API_REPO_KEY")
        ci_run = CIRun()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            ci_run.create_main()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

        self.logger_mock.error.assert_called_with(
            "ERROR: No EMBEDOPS_API_REPO_KEY envvar found"
        )

    def test_successful_call(self):
        expected_id = "yabbazabba"
        new_ci_run = MagicMock()
        new_ci_run.id = expected_id
        self.ci_run_caller.return_value = new_ci_run
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create_entry()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        self.ci_run_caller.assert_called_with("memusage", "abcd1234", "main")
        self.logger_mock.info.assert_called_with(expected_id)


from os import getenv
import importlib


class TestSwaggerCall:
    @pytest.fixture(autouse=True)
    def configure_env(self, monkeypatch, mocker):
        self.expected_host = "https://dev-01.embedops.io"
        self.expected_type = "memusage"
        self.expected_commit_id = "deadb00f"
        self.expected_branch = "main"
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("EMBEDOPS_HOST", self.expected_host)
        monkeypatch.setenv("EMBEDOPS_API_REPO_KEY", "special_pwefix")
        monkeypatch.setenv("EMBEDOPS_ANALYSIS_TYPE", self.expected_type)
        monkeypatch.setenv("BITBUCKET_COMMIT", self.expected_commit_id)
        monkeypatch.setenv("BITBUCKET_BRANCH", self.expected_branch)
        monkeypatch.setenv(
            "BITBUCKET_GIT_HTTP_ORIGIN", "http://bitbucket.org/dojofive/embedops-tools"
        )
        monkeypatch.setenv("BITBUCKET_BUILD_NUMBER", "10")
        monkeypatch.setenv("BITBUCKET_STEP_UUID", "yoo-yoo-eye-de")
        self.logger_mock = mocker.patch("embedops_cli.eotools.ci_run._logger")

        self.ci_run = CIRun()
        yield
        del self.ci_run


    def test_successful_create_response(self, mocker):
        mocked_id = "123123"
        ci_run = MagicMock()
        ci_run.id = mocked_id

        get_client = mocker.patch("embedops_cli.eotools.ci_run.get_client")

        get_client().create_ci_run_from_ci.return_value = ci_run

        response = self.ci_run.create("memusage", "deadb00f", "main")
        assert response.id == mocked_id

    def test_failed_create_response(self, mocker):

        get_client = mocker.patch("embedops_cli.eotools.ci_run.get_client")

        get_client().create_ci_run_from_ci.side_effect = ValueError("garbage!")
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create_entry()
        self.logger_mock.error.assert_called_with("garbage!")

        get_client().create_ci_run_from_ci.side_effect = TypeError("trash!")
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create_entry()
        self.logger_mock.error.assert_called_with("trash!")

        get_client().create_ci_run_from_ci.side_effect = rest.ApiException("refuse!")
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create_entry()
        self.logger_mock.error.assert_called_with("refuse!")

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
