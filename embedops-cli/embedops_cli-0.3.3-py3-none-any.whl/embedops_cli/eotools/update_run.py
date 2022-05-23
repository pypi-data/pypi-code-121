"""A module to handle updating a CI run's sdtatus"""
from logging import getLogger
from sys import stdin
from embedops_cli.config import settings

# import embedops_cli.api as api_lib
from embedops_cli.api import ApiClient, CIRunUpdateProps, Configuration

_logger = getLogger(__name__)


class CiRun:
    """A class for updating the status of a CI run depending on the status of the current CI job"""

    @staticmethod
    def _update_ci_run(status_str):

        try:
            configuration = Configuration()
            configuration.api_key["X-API-Key"] = settings.api_repo_key
            configuration.host = f"{settings.host}/api/v1"

            # create an instance of the API class
            api_instance = ApiClient(configuration)
            ci_run = CIRunUpdateProps()
            ci_run.status = status_str
            ci_run.pipeline_url = settings.job_url
            updated_run = api_instance.update_ci_run_from_ci(ci_run, settings.run_id)

            _logger.debug("Updated CI run:")
            _logger.debug(updated_run)

            del api_instance  # kills the thread pool
        except AttributeError as exc:
            _logger.info("No API Repo Key provided. CI run will not be updated.")
            _logger.info(exc)

    @staticmethod
    def _previous_return():
        return int(stdin.readline())

    def finalize_ci_run(self):
        """Update the status of the current CI run based on the value of a standard in read"""
        previous_return = self._previous_return()
        if previous_return != 0:
            self._update_ci_run("failure")
        else:
            self._update_ci_run("success")


def main():
    """Entrypoint for the `eotools-update-run` tool"""
    ci_run = CiRun()
    ci_run.finalize_ci_run()
