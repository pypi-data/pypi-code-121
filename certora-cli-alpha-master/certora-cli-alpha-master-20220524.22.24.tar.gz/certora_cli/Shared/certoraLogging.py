import argparse
import logging
import sys
import typing
from typing import Dict, Any
import atexit
from pathlib import Path

from Shared.certoraUtils import Singleton, write_json_file, red_text, orange_text

RESOURCE_ERRORS_FILE_PATH = Path("resource_errors.json")


class ColoredString(logging.Formatter):
    def __init__(self, msg_fmt: str = "%(name)s - %(message)s") -> None:
        super().__init__(msg_fmt)

    def format(self, record: logging.LogRecord) -> str:
        to_ret = super().format(record)
        if record.levelno == logging.WARN:
            return orange_text("WARNING") + ": " + to_ret
        elif record.levelno >= logging.ERROR:  # aka ERROR, FATAL, and CRITICAL
            return red_text(record.levelname) + ": " + to_ret
        else:  # aka WARNING, INFO, and DEBUG
            return record.levelname + ": " + to_ret


class TopicFilter(logging.Filter):
    def __init__(self, names: typing.Iterable[str]) -> None:
        super().__init__()
        self.logged_names = set(names)

    def filter(self, record: logging.LogRecord) -> bool:
        return (record.name in self.logged_names) or record.levelno >= logging.WARN


class ResourceErrorHandler(logging.NullHandler, metaclass=Singleton):
    """
    A handler that creates a JSON error report for all problems concerning resources, like Solidity and spec files.
    The handler gathers log messages, filters them, and maintain a local data state.
    To generate the report, dump_to_log must be called. It should be called in the shutdown code of certoraRun.py
    This class is a Singleton, which should prevent most concurrency issues.
    ~~~~
    Filter logic:
    We only care about messages with a topic in resource topics, that are of logging level CRITICAL.
    We prettify the message string itself to be concise and less verbose.
    TODO - fetch typechecking errors from a file. The typechecking jar should generate an errors file, giving us more
    control.
    Note - we have no choice but to filter SOLC errors, for example.
    """
    resource_topics = ["solc", "type_check"]

    '''
    errors_info is a JSON object that should look like this:
    {
        "topics": [
            {
                "name": "",
                "messages": [
                    {
                        "message": "",
                        "location": []
                    }
                ]
            }
        ]
    }
    '''
    errors_info: Dict[str, Any] = {
        "topics": []
    }

    # ~~~ Message editing constants
    '''
    If one of this identifiers is present in the message, we log it. This is to avoid superfluous messages like
    "typechecking failed".
    "Severe compiler warning:" is there to handle errors originating from certoraBuild.check_for_errors_and_warnings()
    '''
    error_identifiers = ["Syntax error", "Severe compiler warning:", "error:\n"]

    # We delete these prefixes and everything that came before them
    prefix_delimiters = ["ERROR ALWAYS - ", "ParserError:\n", "error:\n"]

    def __init__(self) -> None:
        super(ResourceErrorHandler, self).__init__()

    def handle(self, record: logging.LogRecord) -> bool:
        if (record.name in self.resource_topics) and record.levelno >= logging.CRITICAL:
            message = record.getMessage()
            for identifier in self.error_identifiers:
                if identifier in message:
                    for delimiter in self.prefix_delimiters:
                        if delimiter in message:
                            message = message.split(delimiter)[1].strip()

                    message = message.splitlines()[0]  # Removing all but the first remaining line

                    # Adding the message to errors_info
                    error_dict = {
                        "message": message,
                        "location": []  # TODO - add location in the future, at least for Syntax errors
                    }

                    topic_found = False
                    for topic in self.errors_info["topics"]:
                        if topic["name"] == record.name:
                            topic["messages"].append(error_dict)
                            topic_found = True
                            break

                    if not topic_found:
                        topic_dict = {
                            "name": record.name,
                            "messages": [
                                error_dict
                            ]
                        }
                        self.errors_info["topics"].append(topic_dict)

                    break  # Do not log the same error twice, even if it has more than one identifier
        return True

    def dump_to_log(self) -> None:
        write_json_file(self.errors_info, RESOURCE_ERRORS_FILE_PATH)


def logging_setup(quiet: bool = False, debug: typing.Optional[str] = None, debug_topics: bool = False) -> None:
    root_logger = logging.root

    root_logger.addHandler(ResourceErrorHandler())

    stdout_handler = logging.StreamHandler(stream=sys.stdout)

    if debug_topics:
        base_message = "%(name)s - %(message)s"
    else:
        base_message = "%(message)s"
    root_logger.addHandler(stdout_handler)
    if sys.stdout.isatty():
        stdout_handler.setFormatter(ColoredString(base_message))
    else:
        stdout_handler.setFormatter(logging.Formatter(f'%(levelname)s: {base_message}'))

    if quiet:
        root_logger.setLevel(logging.ERROR)
    elif debug is None:
        root_logger.setLevel(logging.WARNING)
    else:
        root_logger.setLevel(logging.DEBUG)
        if debug != "":
            names = [n.strip() for n in debug.split(",")]
            stdout_handler.addFilter(TopicFilter(names))


def setup_log_arguments(args: argparse.Namespace) -> None:
    logging_setup(args.short_output, args.debug, args.debug_topics)


@atexit.register
def logging_shutdown() -> None:
    try:
        ResourceErrorHandler().dump_to_log()  # Calling the Singleton handler class
    except Exception:  # As this function is always called at exit, we must be very careful about exceptions it raises
        # We should not rely on the ResourceErrorHandler to handle the error below, but other logger should work fine
        logging.warning("Could not create resource errors file")
