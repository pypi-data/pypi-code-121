"""Reports the results of a CI run's test stage"""

import sys
from pprint import pformat
from logging import getLogger
from embedops_cli.config import settings
from embedops_cli.utilities import post_dict

_logger = getLogger(__name__)


def post_test_report(filename):
    """Post the contents of the test run file to the metrics API"""
    try:
        headers = {
            "X-API-Key": settings.api_repo_key,
        }
    except AttributeError as exc:
        _logger.info("No API Repo Key provided. Report will not be sent.")
        _logger.info(exc)
        sys.exit(1)

    data = {"type": "junit"}
    with open(filename, "rb") as file_obj:
        files = {
            "data": (
                filename,
                file_obj,
                "application/xml+junit",
            )
        }

        response = post_dict(
            settings.ci_artifact_endpoint,
            data_dict=data,
            file_dict=files,
            headers=headers,
        )

    if response.status_code != 200:
        _logger.error(
            (
                f"\nFAILING: Expected response type {200}(Created)"
                f"from ci run artifact endpoint, got {response.status_code}"
            )
        )
        response_string = pformat(response.json(), indent=4)
        _logger.error(response_string)
        sys.exit(1)

    response_string = pformat(response.json(), indent=4)
    _logger.info(response_string)


def main():
    """Entrypoint for artifact creation"""
    post_test_report(settings.test_output)
