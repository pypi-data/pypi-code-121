import os
from pluggy import HookimplMarker

from _pistar.config import Config
from _pistar.utilities.argument_parser import ArgumentTypeError

hookimpl = HookimplMarker("pistar")


class COMMANDS:
    GENERATE = "generate"
    EXECUTE = "run"


def case_timeout_option_type(_string):
    _string = _string.strip()
    if _string.isdigit() and int(_string) != 0:
        return _string
    else:
        raise ArgumentTypeError(f"invalid value: {_string}, a positive integer needed")


@hookimpl(tryfirst=True)
def pistar_add_option(config: Config):
    config.add_option(
        "files_or_dir",
        action="store",
        nargs="+",
        type=str,
        metavar="files_or_dir",
        help="Specify a list or directory of test case files",
    )
    config.add_option(
        "--type",
        action="store",
        type=str,
        default="pistar",
        choices=["pistar", "pytest"],
        required=False,
        help="Specify the type of test case, the default value is pistar",
    )
    config.add_option(
        "-o",
        "--output",
        action="store",
        type=str,
        required=False,
        default=os.curdir,
        metavar="",
        help="Specify the result output directory",
    )
    config.add_option(
        "--debug",
        action="store_true",
        help="Record pistar framework log",
    )
    config.add_option(
        "--collectonly",
        action="store_true",
        help="Only collect test cases without executing them.",
    )
    config.add_option(
        "--nocolor",
        action="store_true",
        help="Print info without color"
    )

    config.add_option(
        "--case_timeout",
        type=case_timeout_option_type,
        action="store",
        help="Just specify the timeout seconds for each use case."
    )
