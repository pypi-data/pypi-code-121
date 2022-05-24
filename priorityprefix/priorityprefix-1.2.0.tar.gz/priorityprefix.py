

import logging
import sys
import warnings


__version__ = "1.2.0"

SD_EMERG = 0
SD_ALERT = 1
SD_CRIT = 2
SD_ERR = 3
SD_WARNING = 4
SD_NOTICE = 5
SD_INFO = 6
SD_DEBUG = 7


def level_to_priority(level):
    if level > 45:
        return SD_CRIT
    if level > 35:
        return SD_ERR
    if level > 25:
        return SD_WARNING
    if level > 15:
        return SD_INFO
    return SD_DEBUG


class FormattingWrapper:

    def __init__(self, child_formatter):
        self.child = child_formatter

    def annotate(self, levelno, text):
        priority = level_to_priority(levelno)
        return prefix_all_lines(priority, text)

    def format(self, record):
        unprefixed = self.child.format(record)
        return self.annotate(record.levelno, unprefixed)


def prefix_all_lines(priority, block_of_text):
    prefixed = "\n".join(
        "<%i>%s" % (priority, line)
        for line in block_of_text.splitlines()
    )
    if block_of_text.endswith("\n"):
        prefixed = prefixed + "\n"
    return prefixed


def excepthook(exc_type, exc_value, exc_tb):
    import traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    prefixed_tb_text = prefix_all_lines(SD_ERR, "\n".join(tb_lines))
    sys.stderr.write(prefixed_tb_text)


def formatwarning(message, category, filename, lineno, line=None):
    msg = warnings.WarningMessage(message, category, filename, lineno, None, line)
    original = warnings._formatwarnmsg_impl(msg)
    return prefix_all_lines(SD_WARNING, original)


def install(logger=None, sysexcepthook=True, warningsformat=True):
    if logger is None:
        logger = logging.root
    for handler in logger.handlers:
        handler.formatter = FormattingWrapper(handler.formatter)
    if sysexcepthook:
        sys.excepthook = excepthook
    if warningsformat:
        warnings.formatwarning = formatwarning
