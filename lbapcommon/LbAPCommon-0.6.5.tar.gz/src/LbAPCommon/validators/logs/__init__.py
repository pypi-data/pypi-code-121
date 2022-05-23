###############################################################################
# (c) Copyright 2020-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

__all__ = [
    "count_log_messages",
    "parse_log",
]

import re
from collections import defaultdict

import pkg_resources
import yaml

MESSAGE_RE = re.compile(
    r"(# )?(?:(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+) )?([^\s]+)\s*"
    r"(VERBOSE|DEBUG|INFO|WARNING|ERROR|FATAL|ALWAYS|SUCCESS) +([^\n]+)"
)


known_messages = yaml.safe_load(
    pkg_resources.resource_string(
        "LbAPCommon", "validators/logs/data/known_messages.yaml"
    ).decode()
)


def count_log_messages(log_text):
    """Parse the log text for errors and advice.

    Args:
        log_text (str): Contents of the log file.

    Returns:
        tuple[int]: Tuple containing the number of WARNING/ERROR/FATAL level messages in
        the job log
    """
    log_messages = _split_by_level(log_text)

    n_warning = len(log_messages["WARNING"])
    n_error = len(log_messages["ERROR"])
    n_fatal = len(log_messages["FATAL"])

    return (n_warning, n_error, n_fatal)


def explain_log(log_text):
    """Splits a Gaudi job log by message level.

    Args:
        log_text (str): Contents of the log file.

    Raises:
        NotImplementedError: when a check is not implemented

    Returns:
        tuple[dict[list[int]]]:
            A tuple of three dictionaries corresponding to (explanations,
            suggestion, error) where each is a dictionary of
            messages to a list of log file line numbers.
    """
    log_messages = _split_by_level(log_text)

    explanations = defaultdict(list)
    suggestions = defaultdict(list)
    errors = defaultdict(list)

    for check in known_messages["full_checks"]:
        if re.search(check["regex"], log_text):
            if check.get("fatal", False):
                errors[check["details"]] = None
            else:
                suggestions[check["details"]] = None

    for check in known_messages["line_checks"]:
        if "regex" in check:
            check_func = re.compile(r"^" + check["regex"] + r"$").match
        elif "message" in check:
            check_func = lambda s: check["message"] == s  # NOQA
        else:
            raise NotImplementedError(check)

        for line_no, _, _, _, message in log_messages[check["level"]]:
            if check_func(message):
                if check.get("fatal", False):
                    errors[check["details"]].append(line_no)
                elif not check.get("ignore", False):
                    suggestions[check["details"]].append(line_no)
                else:
                    explanations[check["details"]].append(line_no)

    return list(explanations.items()), list(suggestions.items()), list(errors.items())


def _split_by_level(log_text):
    """Splits a Gaudi job log by message level.

    Args:
        log_text (str): Contents of the log file

    Returns:
        dict[list[tuple]]: Dictionary split by log level. Each element in a list of matched log
        lines of the form (line_no, prefix, timestamp, service, message).
    """
    log_messages = defaultdict(list)

    for i, line in enumerate(log_text.split("\n"), start=1):
        match = MESSAGE_RE.match(line)
        if match:
            prefix, timestamp, service, level, message = match.groups()
            log_messages[level].append((i, prefix, timestamp, service, message))
    return log_messages
