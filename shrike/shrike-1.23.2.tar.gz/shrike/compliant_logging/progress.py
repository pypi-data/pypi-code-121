# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Compliant variant of tqdm.
"""


from tqdm import tqdm
from tqdm.utils import disp_len, _unicode
from typing import Iterable, Optional, Union
from io import TextIOWrapper, StringIO
import sys

from shrike.compliant_logging.constants import DataCategory
from shrike.compliant_logging.logging import is_eyesoff, get_prefix

# https://stackoverflow.com/a/65655249
# Number = Union[float, int]

# https://stackoverflow.com/a/50928627
# int --> float


class compliant_tqdm(tqdm):
    """
    Compliant `tqdm` wrapper. In order to prevent scrubbing of the `tqdm`
    progress bar in the eyes-off setting, this wrapper behaves differently when
    `category=DataCategory.PUBLIC` and the environment is eyes-off. In that
    case, the progress bar uses the `"SystemLog:"` prefix (used for system
    metadata that are not scrubbed), and it avoids the use of the carriage
    return (i.e., `"\r"`) prefix when displaying the progress bar, resulting in
    it not updating in place, but rather printing an updated bar in a new line.
    If `category=DataCategory.PRIVATE` (or the environment is eyes-on) then this
    wrapper behaves identically to `tqdm`.

    The simplest way to change the bar prefix is to use this argument when
    constructing it: `bar_format="SystemLog: {l_bar}{bar}{r_bar}"`.
    """

    def __init__(
        self,
        iterable: Optional[Iterable] = None,
        desc: Optional[str] = None,
        total: Optional[float] = None,
        leave: bool = True,
        file: Union[StringIO, TextIOWrapper, None] = None,
        ncols: Optional[int] = None,
        mininterval: Optional[float] = 0.1,
        maxinterval: Optional[float] = 10.0,
        miniters: Optional[float] = None,
        ascii: Union[bool, str, None] = None,
        disable: bool = False,
        unit: str = "it",
        unit_scale: Union[bool, float] = False,
        dynamic_ncols: bool = False,
        smoothing: float = 0.3,
        bar_format: Optional[str] = None,
        initial: float = 0,
        position: Optional[int] = None,
        postfix: Optional[dict] = None,
        unit_divisor: float = 1000,
        write_bytes: Optional[bool] = None,
        lock_args=None,
        nrows: Optional[int] = None,
        colour: Optional[str] = None,
        delay: Optional[float] = 0,
        gui: bool = False,
        category: DataCategory = DataCategory.PRIVATE,
        **kwargs,
    ):
        """
        Parameters:

        - `iterable: iterable`, optional. Iterable to decorate with a
          progressbar. Leave blank to manually manage the updates.
        - `desc: str`, optional. Prefix for the progressbar.
        - `total: int or float`, optional. The number of expected iterations. If
          unspecified, `len(iterable)` is used if possible. If `float("inf")` or
          as a last resort, only basic progress statistics are displayed. (no
          ETA, no progressbar). If `gui` is `True` and this parameter needs
          subsequent updating, specify an initial arbitrary large positive
          number, e.g. `9e9`.
        - `leave: bool`, optional. If `[default: True]`, keeps all traces of the
          progressbar upon termination of iteration. If `None`, will leave only
          if `position` is `0`.
        - `file: io.TextIOWrapper or io.StringIO`, optional. Specifies where to
          output the progress messages (default: `sys.stderr`). Uses
          `file.write(str)` and `file.flush()` methods. For encoding, see
          `write_bytes`.
        - `ncols: int`, optional. The width of the entire output message. If
          specified, dynamically resizes the progressbar to stay within this
          bound. If unspecified, attempts to use environment width. The fallback
          is a meter width of 10 and no limit for the counter and statistics. If
          0, will not print any meter (only stats).
        - `mininterval: float`, optional. Minimum progress display update
          interval [default: 0.1] seconds.
        - `maxinterval: float`, optional. Maximum progress display update
          interval [default: 10] seconds. Automatically adjusts `miniters` to
          correspond to `mininterval` after long display update lag. Only works
          if `dynamic_miniters` or monitor thread is enabled.
        - `miniters: int or float`, optional. Minimum progress display update
          interval, in iterations. If 0 and `dynamic_miniters`, will
          automatically adjust to equal `mininterval` (more CPU efficient, good
          for tight loops). If > 0, will skip display of specified number of
          iterations. Tweak this and `mininterval` to get very efficient loops.
          If your progress is erratic with both fast and slow iterations
          (network, skipping items, etc) you should set `miniters=1`.
        - `ascii: bool or str`, optional. If unspecified or False, use unicode
          (smooth blocks) to fill the meter. The fallback is to use ASCII
          characters `"123456789#"`.
        - `disable: bool`, optional. Whether to disable the entire progressbar
          wrapper [default: False]. If set to None, disable on non-TTY.
        - `unit: str`, optional. String that will be used to define the unit of
          each iteration [default: it].
        - `unit_scale: bool or int or float`, optional. If 1 or True, the number
          of iterations will be reduced/scaled automatically and a metric prefix
          following the International System of Units standard will be added
          (kilo, mega, etc.) [default: False]. If any other non-zero number,
          will scale `total` and `n`.
        - `dynamic_ncols: bool`, optional. If set, constantly alters `ncols` and
          `nrows` to the environment (allowing for window resizes) [default:
          False].
        - `smoothing`: float`, optional. Exponential moving average smoothing
          factor for speed estimates (ignored in GUI mode). Ranges from 0
          (average speed) to 1 (current/instantaneous speed) [default: 0.3].
        - `bar_format: str`, optional. Specify a custom bar string formatting.
          May impact performance. [default: '{l_bar}{bar}{r_bar}'], where
          `l_bar='{desc}: {percentage:3.0f}%|'` and
          `r_bar='| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, '`
          `'{rate_fmt}{postfix}]'`.
          Possible vars: `l_bar`, `bar`, `r_bar`, `n`, `n_fmt`, `total`,
          `total_fmt`, `percentage`, `elapsed`, `elapsed_s`, `ncols`, `nrows`,
          `desc`, `unit`, `rate`, `rate_fmt`, `rate_noinv`, `rate_noinv_fmt`,
          `rate_inv`, `rate_inv_fmt`, `postfix`, `unit_divisor`, `remaining`,
          `remaining_s`, eta. Note that a trailing ": " is automatically removed
          after `{desc}` if the latter is empty.
        - `initial: int or float`, optional. The initial counter value. Useful
          when restarting a progress bar [default: 0]. If using float, consider
          specifying `{n:.3f}` or similar in `bar_format`, or specifying
          `unit_scale`.
        - `position: int`, optional. Specify the line offset to print this bar
          (starting from 0). Automatic if unspecified. Useful to manage multiple
          bars at once (eg, from threads).
        - `postfix: dict or *`, optional. Specify additional stats to display at
          the end of the bar. Calls `set_postfix(**postfix)` if possible (dict).
        - `unit_divisor: float`, optional. [default: 1000], ignored unless
          `unit_scale` is True.
        - `write_bytes: bool`, optional. If (default: None) and `file` is
          unspecified, bytes will be written in Python 2. If `True` will also
          write bytes. In all other cases will default to unicode.
        - `lock_args: tuple`, optional. Passed to `refresh` for intermediate
          output (initialisation, iterating, and updating).
        - `nrows: int`, optional. The screen height. If specified, hides nested
          bars outside this bound. If unspecified, attempts to use environment
          height. The fallback is 20.
        - `colour: str`, optional. Bar colour (e.g. 'green', `'#00ff00'`).
        - `delay: float`, optional. Don't display until [default: 0] seconds
          have elapsed.
        - gui: bool`, optional. WARNING: internal parameter - do not use. Use
          `tqdm.gui.tqdm(...)` instead. If set, will attempt to use matplotlib
          animations for a graphical output [default: False].
        """

        if category == DataCategory.PUBLIC and is_eyesoff():
            if not bar_format:
                bar_format = "{l_bar}{bar}{r_bar}"
            bar_format = f"{get_prefix()}{bar_format}"

        super().__init__(
            iterable=iterable,
            desc=desc,
            total=total,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=mininterval,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            disable=disable,
            unit=unit,
            unit_scale=unit_scale,
            dynamic_ncols=dynamic_ncols,
            smoothing=smoothing,
            bar_format=bar_format,
            initial=initial,
            position=position,
            postfix=postfix,
            unit_divisor=unit_divisor,
            write_bytes=write_bytes,
            lock_args=lock_args,
            nrows=nrows,
            colour=colour,
            delay=delay,
            gui=gui,
            **kwargs,
        )

    @staticmethod
    def status_printer(file):
        fp = file
        fp_flush = getattr(fp, "flush", lambda: None)  # pragma: no cover
        if fp in (sys.stderr, sys.stdout):
            sys.stderr.flush()
            sys.stdout.flush()

        def fp_write(value: str) -> None:
            fp.write(_unicode(value))
            fp_flush()

        last_len = [0]

        prefix = get_prefix()

        def print_status(status: str) -> None:
            fp_write(f"{prefix} ")
            if prefix and status.startswith(prefix):
                fp_write(f"{status}\n")
            else:
                len_s = disp_len(status)
                fp_write("\r" + status + (" " * max(last_len[0] - len_s, 0)))
                last_len[0] = len_s

        return print_status
