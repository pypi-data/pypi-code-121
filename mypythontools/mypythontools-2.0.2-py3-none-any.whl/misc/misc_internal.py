"""Module with functions for 'misc' subpackage."""

from __future__ import annotations
from typing import Callable, Any, Iterable
import builtins
import time
import sys
from pathlib import Path
import os
import shutil

from typing_extensions import Literal
import pandas as pd
from tabulate import tabulate

from ..paths import PathLike, validate_path


class Emojis:
    """Emojis that can be printed."""

    PARTY = "🎉"  # "\U0001F389"
    DISAPPOINTMENT = " ☹️ "  # "\U0001F641"


EMOJIS = Emojis()


class GlobalVars:
    """Global variables that can be useful."""

    @property
    def jupyter(self):
        """If runs in Jupyter, it returns True."""
        return True if hasattr(builtins, "__IPYTHON__") else False

    @property
    def is_tested(self):
        """If is tested with Pytest, it returns True."""
        return True if "PYTEST_CURRENT_TEST" in os.environ else False


GLOBAL_VARS = GlobalVars()

DEFAULT_TABLE_FORMAT = {
    "tablefmt": "grid",
    "floatfmt": ".3f",
    "numalign": "center",
    "stralign": "center",
}


class TimeTable:
    """Class that create printable table with spent time on various phases that runs sequentionally.

    Add entry when current phase end (not when it starts).

    Example:
        >>> import time
        ...
        >>> time_table = TimeTable()
        >>> time.sleep(0.01)
        >>> time_table.add_entry("First phase")
        >>> time.sleep(0.02)
        >>> time_table.add_entry("Second phase")
        >>> time_table.add_entry("Third phase")
        >>> time_table.finish_table()
        ...
        >>> print(time_table.time_table)
        +--------------+--------------+
        |     Time     |  Phase name  |
        +==============+==============+
        | First phase  |    0...
    """

    def __init__(self) -> None:
        """Init the table."""
        self.time_df: pd.DataFrame = pd.DataFrame()
        self.time_table: str = ""
        self.times: list[tuple[str, float]] = []
        self.last_time: float = time.time()

    def add_entry(self, phase_name: str) -> None:
        """Add new line to the Time table."""
        self.times.append((phase_name, round((time.time() - self.last_time), 3)))

    def finish_table(self, table_format: None | dict = None) -> None:
        """Create time table.

        Args:
            table_format (None | dict, optional): Dict of format settings used in tabulate. If None, default
                DEFAULT_TABLE_FORMAT is used. Defaults to None.
        """
        if not table_format:
            table_format = DEFAULT_TABLE_FORMAT

        self.add_entry("Completed")
        self.time_df = pd.DataFrame(self.times, columns=["Time", "Phase name"])
        self.time_table = tabulate(self.time_df.values, headers=list(self.time_df.columns), **table_format)


def watchdog(timeout: int | float, function: Callable, *args, **kwargs) -> Any:
    """Time-limited execution for python function. TimeoutError raised if not finished during defined time.

    Args:
        timeout (int | float): Max time execution in seconds.
        function (Callable): Function that will be evaluated.
        *args: Args for the function.
        *kwargs: Kwargs for the function.

    Raises:
        TimeoutError: If defined time runs out.
        RuntimeError: If function call with defined params fails.

    Returns:
        Any: Depends on used function.

    Examples:
        >>> import time
        >>> def sleep(sec):
        ...     for _ in range(sec):
        ...         time.sleep(1)
        >>> watchdog(1, sleep, 0)
        >>> watchdog(1, sleep, 10)
        Traceback (most recent call last):
        TimeoutError: ...
    """
    old_tracer = sys.gettrace()

    def tracer(frame, event, arg, start=time.time()):
        """Sys trace helpers that checks the time for watchdog."""
        now = time.time()
        if now > start + timeout:
            raise TimeoutError("Time exceeded")
        return tracer if event == "call" else None

    try:
        sys.settrace(tracer)
        result = function(*args, **kwargs)

    except TimeoutError:
        sys.settrace(old_tracer)
        raise TimeoutError(
            "Timeout defined in watchdog exceeded.",
        )

    except Exception as err:
        sys.settrace(old_tracer)
        raise RuntimeError(
            f"Watchdog with function {function.__name__}, args {args} and kwargs {kwargs} failed."
        ) from err

    finally:
        sys.settrace(old_tracer)

    return result


def delete_files(paths: PathLike | Iterable[PathLike], on_error: Literal["pass", "raise"] = "pass"):
    """Delete file, folder or Sequence of files or folders.

    Folder can contain files, it will be also recursively deleted. You can choose behavior on error (because
    of permissions for example).

    Args:
        paths (PathLike | Iterable[PathLike]): List or tuple of paths to be deleted. Can be files as well
            as folders.
        on_error (Literal["pass", "raise"], optional): Depends whether you want to pass or raise an error.
            Error can occur when for example file is opened or if has no necessary permissions.
            Defaults to "pass".
    """
    if isinstance(paths, (Path, str, os.PathLike)):
        paths = [paths]

    for i in paths:
        try:
            delete_path = Path(i)

            if delete_path.exists():
                if delete_path.is_dir():
                    shutil.rmtree(delete_path, ignore_errors=False)
                else:
                    delete_path.unlink()

        except (FileNotFoundError, OSError):
            if on_error == "raise":
                raise


def print_progress(name: str, verbose: bool = True):
    """Print current step of some process.

    Divide it with newlines so it's more readable.

    Args:
        name (str): Name current step.
        verbose (bool): It is possible to turn off logging of progress with one parameter config value.
            Defaults to True.
    """
    if verbose:
        print(f"\n{name}\n")
