#!/usr/bin/env python
"""
`ci_run.py`
=======================================================================
A small script to create and update EmbedOps CI run records
* Author(s): Bryan Siepert
"""
import sys
import importlib
import logging
from os import getenv
from embedops_cli.api import (
    Configuration,
    DefaultApi as ApiClient,
    CIRunCreateProps,
    CIRunUpdateProps,
    rest,
)
from embedops_cli.api import get_client
import embedops_cli.config

_logger = logging.getLogger("create_run")


class CIRun:
    """A wrapper for creating and updating CIRun records"""

    def __init__(self):
        # pylint: disable=import-outside-toplevel

        importlib.reload(embedops_cli.config)
        self._settings = embedops_cli.config.settings

    # create().id
    def create_main(self):
        """The main entrypoint for the module, to allow for binary-izing"""

        env_error = False

        if getenv("CI") is None or getenv("CI") != "true":
            _logger.info("LOCAL")
            sys.exit(0)

        if self._settings.get("commit") is None:
            _logger.error("ERROR: No commit id envvar found")
            env_error = True

        if self._settings.get("branch") is None:
            _logger.error("ERROR: No branch name envvar found")
            env_error = True

        if self._settings.get("analysis_type") is None:
            _logger.error("ERROR: No analysis type envvar found")
            env_error = True

        if self._settings.get("api_repo_key") is None:
            _logger.error("ERROR: No EMBEDOPS_API_REPO_KEY envvar found")
            env_error = True

        if env_error is True:
            sys.exit(1)

        analysis_type = self._settings.analysis_type
        commit_id = self._settings.commit
        branch_name = self._settings.branch

        return self.create(analysis_type, commit_id, branch_name)

    @staticmethod
    def create(analysis_type, commit_id, branch_name):

        """Use the branch name, commit sha, and analysis type to create a new ciRun instance"""

        api_client = get_client()
        create_properties = CIRunCreateProps(
            branch=branch_name, commit_id=commit_id, type=analysis_type
        )

        response = None

        try:
            response = api_client.create_ci_run_from_ci(create_properties)
        except (ValueError, TypeError, rest.ApiException) as err:
            _logger.error(err.args[0])
            sys.exit(1)
        finally:
            # this kills the thread pool so the process can exit
            del api_client
        return response

    def _update_ci_run(self, status_str):

        try:
            configuration = Configuration()
            configuration.api_key["X-API-Key"] = self._settings.api_repo_key
            configuration.host = f"{self._settings.host}/api/v1"

            # create an instance of the API class
            api_instance = ApiClient(configuration)
            ci_run = CIRunUpdateProps()
            ci_run.status = status_str
            ci_run.pipeline_url = self._settings.job_url
            updated_run = api_instance.update_ci_run_from_ci(
                ci_run, self._settings.run_id
            )

            _logger.debug("Updated CI run:")
            _logger.debug(updated_run)

            del api_instance  # kills the thread pool
        except AttributeError as exc:
            _logger.info("No API Repo Key provided. CI run will not be updated.")
            _logger.info(exc)

    @staticmethod
    def _previous_return():
        return int(sys.stdin.readline())

    def finalize_ci_run(self):
        """Update the status of the current CI run based on the value of a standard in read"""
        previous_return = self._previous_return()
        if previous_return != 0:
            self._update_ci_run("failure")
        else:
            self._update_ci_run("success")


def update_entry():
    """Entrypoint for the `eotools-update-run` tool"""
    ci_run = CIRun()
    ci_run.finalize_ci_run()


def create_entry():
    """Entrypoint for the `eotools-create-run` tool"""
    ci_run = CIRun()
    new_ci_run = ci_run.create_main()
    _logger.info(new_ci_run.id)
    sys.exit(0)


if __name__ == "__main__":
    create_entry()
