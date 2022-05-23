import sys
import select

from typing import Iterable, Tuple

from .typing import JSON
from .exceptions import NotConnectedToPipe
from .json_utils import read_json, dump_json


def read_stdin_lines(read_timeout: int = 0) -> Iterable[str]:
    """
    Read stdin line by line and return the tuple:

    (IS_STDIN_PIPE, IS_STDOUT_PIPE, LINE)

    :param read_timeout: read timeout of stdin. 0 = infinite
    :type read_timeout: int
    """

    if sys.stdin.isatty():
        raise NotConnectedToPipe(
            "Input data must be entered as a UNIX pipeline. For example: "
            "'cat info.json | tool-name'")

    is_stdout_pipe = not sys.stdout.isatty()

    # -------------------------------------------------------------------------
    # Read info by stdin or parameter
    # -------------------------------------------------------------------------
    if read_timeout:
        if sys.stdin in select.select([sys.stdin], [], [], read_timeout)[0]:
            for line in sys.stdin.readlines():
                yield is_stdout_pipe, line

        else:
            yield is_stdout_pipe, None

    else:

        while 1:

            line = sys.stdin.readline()

            if not line:
                return

            yield is_stdout_pipe, line


def read_json_from_stdin() -> Iterable[Tuple[bool, JSON]]:
    # Read from the STDIN PIPE
    for _, line in read_stdin_lines():

        try:
            # this var contains JSON data in our format
            yield False, read_json(line)

        except:
            yield True, line


def write_json_to_stdout(
    data: JSON,
    force_flush: bool = True
):
    write_to_stdout(dump_json(data), force_flush=force_flush)


def write_json_to_stderr(data: JSON):
    write_to_stderr(dump_json(data))


def write_to_stdout(data: str, force_flush: bool = True):
    try:
        sys.stdout.write(f"{data}\n")
    except BrokenPipeError as e:
        print(
            f"[ERROR] when try to write data '{data}' in pipe",
            file=sys.stderr,
            flush=True
        )

    if force_flush:
        try:
            sys.stdout.flush()
        except BrokenPipeError:
            ...


def write_to_stderr(data: str):
    sys.stderr.write(f"{data}\n")

    try:
        sys.stderr.flush()
    except BrokenPipeError:
        ...


__all__ = ("read_json_from_stdin", "write_json_to_stdout", "write_to_stdout",
           "write_to_stderr", "write_json_to_stderr",
           "read_stdin_lines")
