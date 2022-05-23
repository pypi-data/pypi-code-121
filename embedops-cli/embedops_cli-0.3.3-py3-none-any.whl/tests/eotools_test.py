"""
`api_interface_test`
=======================================================================
Unit tests for code to upload XML files to the API
* Author(s): Bryan Siepert
"""

import uuid
from unittest.mock import Mock
from embedops_cli.config import settings
from embedops_cli.api import CIRunUpdateProps
from embedops_cli.eotools.update_run import main as update_run_main
from embedops_cli.eotools.create_run import CIRun
import pytest


class FakeResponse:
    """Fake function return"""

    @classmethod
    def ret_zero(cls):
        """Just returns zero"""
        return "0"


class FakeConfig:
    """Fake config class"""

    def __init__(self):
        self._run_id = uuid.uuid1()

    @property
    def run_id(self):
        """Run id for fake config class"""
        return self._run_id

class EOToolsTests:
    @pytest.fixture(autouse=True)
    def configure_env(self, monkeypatch, mocker):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("EMBEDOPS_API_REPO_KEY", "special_pwefix")
        monkeypatch.setenv("EMBEDOPS_ANALYSIS_TYPE", "memusage")
        monkeypatch.setenv("BITBUCKET_COMMIT", "abcd1234")
        monkeypatch.setenv("BITBUCKET_BRANCH", "main")
        self.ci_run_caller = mocker.patch("embedops_cli.eotools.create_run.CIRun.create_run")
        self.logger_mock = mocker.patch("embedops_cli.eotools.create_run._logger")
        self.ci_run = CIRun()
        yield
        del(self.ci_run)

    def test_successful_job_sets_ci_url(self, mocker):

        mocker.patch(
            "embedops_cli.eotools.update_run.CiRun._previous_return", return_value=0
        )

        # create the mock to check how update_ci_run_from_ci is called
        api_client_mock = Mock()
        api_client_mock.update_ci_run_from_ci.return_value = object()

        mocker.patch(
            "embedops_cli.eotools.update_run.ApiClient", return_value=api_client_mock
        )

        update_run_main()

        calls = api_client_mock.update_ci_run_from_ci.call_args_list
        assert len(calls) == 1

        call_args = calls[0][0]
        ci_properties = call_args[0]
        ci_run_id = call_args[1]

        assert isinstance(ci_properties, CIRunUpdateProps)
        assert ci_run_id == settings.run_id
        assert ci_properties.pipeline_url == settings.job_url

    def test_api_client_configured(self, mocker):
    
        self.config_dict = mocker.patch.dict(
            self.config_class.api_key, {"X-API-Key": None}
        )
        api_client = mocker.patch("embedops_cli.api.get_client")
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create_entry()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # This tests that the configuration object's 'api_key' attribute dict's
        # 'X-API-Key' key is set to the specified API key
        self.config_class().api_key.__setitem__.assert_called_with(
            "X-API-Key", "special_pwefix"
        )
        assert self.config_class().host == self.expected_host + "/api/v1"

        args, _kwargs = api_client().create_ci_run_from_ci.call_args
        first_call = args[0]
        assert first_call.type == self.expected_type
        assert first_call.commit_id == self.expected_commit_id
        assert first_call.branch == self.expected_branch