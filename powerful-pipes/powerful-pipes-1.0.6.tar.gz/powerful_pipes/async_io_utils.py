import sys
import builtins

from typing import Iterable, Tuple

from aioconsole import ainput, aprint, get_standard_streams

from .typing import JSON
from .exceptions import NotConnectedToPipe
from .json_utils import read_json, dump_json


async def async_read_stdin_lines(read_timeout: int = 0) -> Iterable[str]:
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
    while True:
        try:
            message = await ainput()

            yield is_stdout_pipe, message

        except EOFError:
            return


async def async_read_json_from_stdin() -> Tuple[bool, JSON]:
    # Read from the STDIN PIPE
    async for has_stdout_pipe, json_line in async_read_stdin_lines():
        try:
            yield False, read_json(json_line)

        except:
            yield True, json_line


async def async_write_json_to_stdout(
        data: JSON,
        force_flush: bool = True
):
    await async_write_to_stdout(dump_json(data), force_flush=force_flush)


async def async_write_json_to_stderr(data: JSON):
    await async_write_to_stderr(dump_json(data))


async def async_write_to_stdout(data: str, force_flush: bool = True):
    try:
        await aprint(data, flush=force_flush)
    except BrokenPipeError as e:
        print(
            f"[ERROR] when try to write data '{data}' in pipe: {e}",
            file=sys.stderr,
            flush=True
        )


async def async_write_to_stderr(data: str):
    if w := getattr(builtins, "cached_async_writer", None):
        writer = w
    else:
        _, writer = await get_standard_streams(use_stderr=True)
        builtins.cached_async_writer = w

    writer.write(f"{data}\n")
    await writer.drain()


__all__ = ("async_read_stdin_lines", "async_read_json_from_stdin",
           "async_write_json_to_stdout", "async_write_json_to_stderr",
           "async_write_to_stdout", "async_write_to_stderr")
