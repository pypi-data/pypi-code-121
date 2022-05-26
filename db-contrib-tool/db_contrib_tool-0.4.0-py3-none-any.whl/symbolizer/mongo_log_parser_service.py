"""Service to parse backtraces in mongo log files."""
import sys
from json import JSONDecodeError, JSONDecoder
from typing import Any, Dict, Optional, Union

import inject


class MongoLogParserService:
    """Service to parse backtraces in mongo log files."""

    @inject.autoparams()
    def __init__(self, json_decoder: JSONDecoder):
        """
        Initialize.

        :param json_decoder: JSONDecoder object.
        """
        self.json_decoder = json_decoder

    def parse_log_lines(self, log_lines: str) -> Optional[Dict[str, Any]]:
        """
        Analyze log lines until backtrace is found.

        :param log_lines: Log lines as string.
        :return: Backtrace dict or None.
        """
        for line in log_lines.splitlines():
            start_index = line.find("{")
            if start_index == -1:
                continue

            # Skip over everything before the first '{' since it is likely to be log line prefixes.
            sub_line = line[start_index:]
            try:
                # Using raw_decode() to ignore extra data after the closing '}' to allow maximal
                # sloppiness in copy-pasting input.
                possible_trace_doc = self.json_decoder.raw_decode(sub_line)[0]

                trace_doc = self.find_backtrace(possible_trace_doc)
                if trace_doc is not None:
                    return trace_doc

            except JSONDecodeError:
                # It is expected that any kind of logs may be passed in along with a backtrace,
                # we are skipping the lines that do not contain a valid JSON document
                pass

        return None

    def find_backtrace(self, log_line: Any) -> Optional[Dict[str, Any]]:
        """
        Search the log line recursively for a dict that has "backtrace" and "processInfo" keys.

        :param log_line: Log line as dict or part of the log line as any type.
        :return: Backtrace dict or None.
        """
        try:
            if "backtrace" in log_line.keys() and "processInfo" in log_line.keys():
                return log_line
            for val in log_line.values():
                res = self.find_backtrace(val)
                if res:
                    return res
        except AttributeError:
            pass
        return None
