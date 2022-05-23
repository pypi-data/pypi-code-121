"""
`api_interface_test`
=======================================================================
Unit tests for code to upload XML files to the API
* Author(s): Bryan Siepert
"""
from embedops_cli.config import settings
from embedops_cli.eotools import post_test_report
import pytest

class FakeResponse(object):
    """Fake http response for test use"""

    status_code = 200

    def json(self):
        """Empty JSON object"""
        return "{}"


# test the cli/click to report_test fn call
class APIInterfaceTest:

    @pytest.fixture(autouse=True)
    def configure_env(self, monkeypatch, mocker):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("EMBEDOPS_API_REPO_KEY", "special_pwefix")
        self.logger_mock = mocker.patch("embedops_cli.eotools.ci_run._logger")

    def test_report_file_contents_sent(self, mocker):
        """test the cli/click to post_test_report fn call"""
        report_filename = "tests/file_fixtures/gtest_failure.xml"
        file_obj = open(report_filename, "rb")
        opn = mocker.patch("embedops_cli.eotools.open")
        opn.return_value = file_obj

        req_mock = mocker.patch("embedops_cli.eotools.post_dict")
        req_mock.return_value = FakeResponse()

        headers = {
            "X-API-Key": settings.api_repo_key,
        }
        data = {"type": "junit"}
        files = {
            "data": (
                report_filename,
                file_obj,
                "application/xml+junit",
            )
        }

        post_test_report(report_filename)
        req_mock.assert_called_with(
            settings.ci_artifact_endpoint, data_dict=data, file_dict=files, headers=headers
    )
