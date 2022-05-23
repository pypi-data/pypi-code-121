#!/usr/bin/env python
"""
`parse.py`
=======================================================================
A script to parse information from build logs
* Author(s): Bryan Siepert
"""
import re
from sys import exit as sys_exit
from os.path import exists as file_exists
from pprint import pformat
import logging

from embedops_cli.config import settings
from embedops_cli.utilities import post_dict, get_compiler
from embedops_cli.eotools.log_parser.iar import SIZE_PATTERN as IAR_SIZE_PATTERN
from embedops_cli.eotools.log_parser.gnu_size_berkeley import (
    SIZE_PATTERN as SIZE_SIZE_PATTERN,
)

_logger = logging.getLogger(__name__)

EXPECTED_RETURN_CODE = 200


def parse_storage_sizes(log_filename, build_size_regex):
    """Check each line in a log file for compiler RAM, flash data, and flash code sizes"""

    build_data = None
    storage_sizes = None
    with open(log_filename, "r", encoding="ascii") as build_log:
        build_data = build_log.read()

    build_results = re.search(build_size_regex, build_data)

    if build_results is None:
        return storage_sizes

    storage_sizes = {
        "flash_code_size": None,
        "flash_data_size": None,
        "ram_size": None,
    }
    storage_sizes["ram_size"] = int(build_results["ram_size"].replace("'", ""))
    storage_sizes["flash_code_size"] = int(
        build_results["flash_code_size"].replace("'", "")
    )
    storage_sizes["flash_data_size"] = int(
        build_results["flash_data_size"].replace("'", "")
    )
    storage_sizes["dimensions"] = {
        "build_target": build_results["build_output_filename"].split("/")[-1]
    }

    # a better solution would be to look for the -g option but it's more complicated
    return storage_sizes


def _report_metrics(build_metrics, run_id, embedops_repo_key):

    headers = {"X-API-Key": embedops_repo_key, "Content-Type": "application/json"}
    if run_id == "LOCAL":
        _logger.info("\nResults:")

    for key in build_metrics:
        if key == "dimensions":
            continue
        stats_data = {
            "ciRunId": run_id,
            "name": key,
            "value": build_metrics[key],
            "dimensions": build_metrics["dimensions"],
        }

        if run_id == "LOCAL":
            _logger.info(f"\t{key} : {pformat(build_metrics[key])}")
        else:
            response = post_dict(
                settings.metrics_endpoint,
                json_dict=stats_data,
                headers=headers,
            )
            # TODO: Refactor this to remove the duplication with similar code in `create_run.py`,
            # perhaps in a shared API library :O
            if response.status_code != EXPECTED_RETURN_CODE:
                _logger.error(
                    f"FAILING: Expected response type {EXPECTED_RETURN_CODE}(Created)"
                    f"from metrics creation endpoint, got {response.status_code}"
                )
                response_string = pformat(response.json(), indent=4)
                _logger.error(response_string)

                sys_exit(1)
            response_string = pformat(response.json(), indent=4)
            _logger.info("Created metric:")
            _logger.info(response_string)


def parse_reports(input_filename, parsing_regex, run_id, embedops_repo_key):
    """Parse the given file for compile sized totals"""
    if not file_exists(input_filename):
        raise FileNotFoundError(
            f"The given input file {input_filename} cannot be found"
        )
    storage_sizes = parse_storage_sizes(input_filename, parsing_regex)
    _logger.info(f"Got storage sizes: {storage_sizes}")
    if storage_sizes is None:
        _logger.error("no build target sizes found")
        sys_exit(1)
    _report_metrics(storage_sizes, run_id, embedops_repo_key)


def main():
    """The main entrypoint for the module, to allow for binary-izing"""
    compiler = get_compiler()
    if compiler == "IAR":
        size_regex = IAR_SIZE_PATTERN
        _logger.info("IAR Pattern loaded")
    elif compiler in ("TI", "GCC"):
        size_regex = SIZE_SIZE_PATTERN
        _logger.info("gnu size pattern loaded for TI and GCC")
    else:
        _logger.warning("EMBEDOPS_COMPILER not set")
        sys_exit(1)
    input_file = settings.input_file
    run_id = settings.run_id

    try:
        api_repo_key = settings.api_repo_key
    except AttributeError:
        api_repo_key = None

    _logger.info(f"EMBEDOPS_INPUT_FILE {input_file}")
    _logger.info(f"EMBEDOPS_RUN_ID {run_id}")

    if run_id is None:
        _logger.warning(
            "EMBEDOPS_RUN_ID not set. Assuming local build, will not push metrics"
        )
        run_id = "LOCAL"
    elif run_id == "LOCAL":
        _logger.info("Local build requested. Will not push metrics")
    elif api_repo_key is None:
        _logger.warning(
            "EMBEDOPS_API_REPO_KEY not set. Assuming local build, will not push metrics."
        )
        run_id = "LOCAL"

    _logger.info("EMBEDOPS_API_REPO_KEY set (not echoing)")

    # this should read directly from settings
    parse_reports(input_file, size_regex, run_id, api_repo_key)


if __name__ == "__main__":
    main()
