"""
Checkstyle plugin for pylint
"""
import argparse
import json
import sys
from itertools import groupby
from typing import Optional, List
from xml.dom import minidom

from pylint.interfaces import IReporter
from pylint.lint.pylinter import PyLinter
from pylint.message import Message
from pylint.reporters.base_reporter import BaseReporter
from pylint.reporters.ureports.nodes import Section
from pylint.typing import MessageLocationTuple


def _create_checkstyle_report(messages: List[Message]) -> str:
    root = minidom.Document()
    checkstyle = root.createElement('checkstyle')
    root.appendChild(checkstyle)
    messages_by_file = {abspath: list(messages)
                        for abspath, messages in
                        (groupby(
                            sorted(messages, key=lambda x: x.abspath),
                            lambda x: x.abspath)
                        )}
    for abspath in messages_by_file:
        file = root.createElement("file")
        file.setAttribute("name", abspath)
        for msg in messages_by_file[abspath]:
            error = root.createElement("error")
            error.setAttribute("line", str(msg.line))
            error.setAttribute("column", str(msg.column))
            error.setAttribute("message", msg.msg)
            error.setAttribute("source", f"{msg.msg_id}:{msg.symbol}")
            error.setAttribute("severity", _map_severity(msg.category))
            file.appendChild(error)
            checkstyle.appendChild(file)
    return root.toprettyxml(indent="  ")


def _map_severity(pylint_category: str) -> str:
    """
    Return a checkstyle severity level based on the pylint category
    Pylint categories:
    https://pylint.pycqa.org/en/latest/user_guide/configuration/all-options.html#evaluation
    Checkstyle severity levels:
    https://checkstyle.sourceforge.io/property_types.html#SeverityLevel
    """
    if pylint_category in ["fatal", "error"]:
        return "error"
    if pylint_category in ["warning", "refactor"]:
        return "warning"
    if pylint_category in ["convention", "info"]:
        return "info"
    return "info"


def json2checkstyle(json_input: str) -> str:
    """
    Convert a json pylint report to checkstyle format
    """
    input_report = json.loads(json_input)
    messages = [
        Message(
            msg_id=item["message-id"],
            symbol=item["symbol"],
            location=MessageLocationTuple(
                abspath=item["path"],
                path=item["path"],
                module=item["module"],
                obj="",
                line=item["line"],
                column=item["column"]),
            msg=item["message"],
            confidence=None
        ) for item in input_report]
    return _create_checkstyle_report(messages)


class CheckstyleReporter(BaseReporter):
    """
    Outputs pylint errors in checkstyle format
    """
    __implements__ = IReporter
    name = "checkstyle"
    extension = "xml"

    def _display(self, layout) -> None:
        pass

    def display_messages(self, layout: Optional[Section]) -> None:
        checkstyle_report = _create_checkstyle_report(self.messages)
        print(checkstyle_report)


def register(linter: PyLinter) -> None:
    """
    Register our reporter as a plugin for pylint
    """
    linter.register_reporter(CheckstyleReporter)


def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert pylint json report to checkstyle")
    parser.add_argument(
        'input',
        metavar='json_input_file',
        type=argparse.FileType('r'),
        nargs='?',
        default=sys.stdin,
        help='Pylint JSON report input file (or stdin)')
    parser.add_argument(
        '-o', '--output',
        metavar='checkstyle_output_file',
        type=argparse.FileType('wb'),
        default=sys.stdout,
        help='Checkstyle report output file (or stdout)')
    return parser


def main():
    """
    Entry point to the CLI for the pylint checkstyle report converter
    """
    parser = _create_argument_parser()
    options = parser.parse_args()
    json_input_file = options.input
    checkstyle_output_file = options.output
    with json_input_file:
        input_report = json_input_file.read()
    checkstyle_report = json2checkstyle(input_report)
    with checkstyle_output_file:
        if 'b' in checkstyle_output_file.mode:
            checkstyle_output_file.write(checkstyle_report.encode("utf-8"))
        else:
            checkstyle_output_file.write(checkstyle_report)


if __name__ == '__main__':
    main()
