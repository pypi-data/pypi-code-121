# ----------------------------------------------------------------------------
# Description    : Logging functionality for the configuration manager client
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import sys
import logging
from typing import Optional


# -- loglevels ---------------------------------------------------------------

# Displayed/logged for -vv.
DEBUG = logging.DEBUG
debug = logging.debug

# Displayed for -v, always logged to file.
INFO = logging.INFO
info = logging.info

# Displayed unless -q, always logged to file.
NOTE = logging.WARNING - 1


def note(*args, **kwargs):
    logging.log(NOTE, *args, **kwargs)


WARN = logging.WARNING
warn = logging.warning

# Displayed unless -qq, always logged to file.
ERROR = logging.ERROR
error = logging.error

# Always displayed and logged. Only use for querying the user, which can be
# disabled with -y.
ALWAYS = logging.CRITICAL
always = logging.critical


# -- functions ---------------------------------------------------------------

class ConsoleHandler(logging.StreamHandler):
    """
    Handler that allows progress information to be printed and retained on the
    last line.
    """

    # ------------------------------------------------------------------------
    def __init__(self, show_progress, *args, **kwargs):
        """
        Initialize console handler.

        Parameters
        ----------
        show_progress: bool
            Show progress.
        """

        super().__init__(*args, **kwargs)
        self.show_progress = show_progress
        self.progress_msg = None

    # ------------------------------------------------------------------------
    def progress(self, message: Optional[str] = None) -> None:
        """
        Sets or clears the progress message.

        Parameters
        ----------
        message: Optional[str]
            If None, clear any existing progress message. Otherwise, add a
            progress message or update the existing one.

        Returns
        -------
        None
        """
        if not self.show_progress:
            return

        stream = self.stream

        if message is not None and self.progress_msg is None:

            # Add progress message.
            stream.write(message)

        elif message is None and self.progress_msg is not None:

            # Clear progress message.
            stream.write("\r")
            stream.write(" " * len(self.progress_msg))
            stream.write("\r")

        elif message != self.progress_msg:

            # Update progress message.
            stream.write("\r")
            stream.write(message)
            stream.write(" " * (len(self.progress_msg) - len(message)))

        self.progress_msg = message
        self.flush()

    # ------------------------------------------------------------------------
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emits a log record.

        Parameters
        ----------
        record: record: Optional[str]
            The record to emit.

        Returns
        -------
        None
        """
        try:
            message = self.format(record)
            stream = self.stream

            if self.progress_msg is not None:

                # Override progress message with log record.
                stream.write("\r")
                stream.write(message)
                stream.write(" " * (len(self.progress_msg) - len(message)))
                stream.write(self.terminator)

                # Write the progress message again on the new line.
                stream.write(self.progress_msg)

            else:

                # Write the message as usual.
                stream.write(message)
                stream.write(self.terminator)

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


# -- globals -----------------------------------------------------------------

# The currently active console handler, to direct progress messages to.
_console_handler = [None]


# -- functions ---------------------------------------------------------------

def configure(verbosity: int, file: Optional[str]) -> None:
    """
    Configures the logging module.

    Parameters
    ----------
    verbosity: int
        Verbosity, ranging from -2 for completely quiet (aside from user
        interaction) to 2 for very verbose.
    file: Optional[str]
        File to log to in addition, using at least verbosity 1.

    Returns
    -------
    None
    """

    # Configure the log levels.
    logging.addLevelName(DEBUG, "debug")
    logging.addLevelName(INFO, "info ")
    logging.addLevelName(NOTE, "note ")
    logging.addLevelName(WARN, "WARN ")
    logging.addLevelName(ERROR, "ERROR")
    logging.addLevelName(ALWAYS, "     ")

    # Determine main loglevel for printing.
    verbosity = min(max(-2, verbosity), 2)
    stdout_level = {
        -2: ALWAYS,
        -1: ERROR,
        0: NOTE,
        1: INFO,
        2: DEBUG}[verbosity]

    # Level for logging to a file is at least INFO, so all pertinent
    # information is logged whether the user wants to see it or not (unless
    # they disabled the log file of course)
    file_level = min(stdout_level, INFO)

    # Figure out the level for the root logger, such that it doesn't filter
    # out anything we need.
    overall_level = stdout_level
    if file is not None:
        overall_level = min(overall_level, file_level)

    # Configure the root logger.
    logger = logging.getLogger()
    logger.setLevel(overall_level)

    # Add the console/stdout handler.
    show_progress = sys.stdout.isatty() and verbosity >= 0
    handler = ConsoleHandler(show_progress)
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.setLevel(stdout_level)
    logger.addHandler(handler)
    _console_handler[0] = handler

    # Add the file handler.
    if file is not None:
        handler = logging.FileHandler(file)
        formatter = logging.Formatter("%(asctime)s %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(file_level)
        logger.addHandler(handler)


# ----------------------------------------------------------------------------
def set_progress_message(message: Optional[str]) -> None:
    """
    Adds, updates, or clears a persistent message displayed at the bottom of
    the terminal. Used for things like progress bars. Only shown when:
     - this module has been configure();
     - stdout appears to be a terminal; and
     - verbosity is nonnegative.

    Parameters
    ----------
    message: Optional[str]
        The message to show, or None to clear it.

    Returns
    -------
    None
    """

    if _console_handler[0] is not None:
        _console_handler[0].progress(message)


# ----------------------------------------------------------------------------
_progress_state = [0]

def progress(fraction: float, message: str) -> None:
    """
    Adds, updates, or clears a progress bar and message displayed at the
    bottom of the terminal. Only shown when:
     - this module has been configure();
     - stdout appears to be a terminal; and
     - verbosity is nonnegative.

    Parameters
    ----------
    fraction: float
        Value between 0 and 1 to indicate progress.
    message: str
        A message to show to the right of the progress bar.

    Returns
    -------
    None
    """

    if _console_handler[0] is None:
        return

    fraction = min(max(0.0, fraction), 1.0)

    SIZE = 20
    filled = int(fraction * SIZE)

    set_progress_message("[{}{}] {:d}% {}.{:<2}".format(
        "#" * filled,
        " " * (SIZE - filled),
        int(fraction * 100),
        message,
        "." * _progress_state[0],
    ))

    _progress_state[0] += 1
    _progress_state[0] %= 3


# ----------------------------------------------------------------------------
def clear_progress() -> None:
    """
    Clears the progress message.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    set_progress_message(None)
