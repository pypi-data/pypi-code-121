"""Logging factory.

Just call setup_logger before use default logging as usual.

Check your log configuration before wasting time here.
Attention: Do not import any project modules or func here (!!!).
"""

import os
import logging
import json

from collections.abc import Mapping
from pathlib import Path

from . import logger
from . import term


def formatter_from_event_type(event_type: int):
    """Map formatter to event."""
    log_styles = {
        logging.NOTSET: term.StyleDefault,
        logging.DEBUG: term.StyleDebug,
        logging.INFO: term.StyleInfo,
        logging.WARNING: term.StyleWarning,
        logging.CRITICAL: term.StyleError,
        logging.ERROR: term.StyleError,
        logging.FATAL: term.StyleError,
    }
    try:
        return log_styles[event_type]
    except (AttributeError, KeyError, IndexError):
        return term.StyleDefault


class Formatter(logger.JSONFormatter):
    """Default log formatter."""

    def format(self, record: logger.LogRecord):
        """Format."""
        super().format(record)

        message = {
            field_name: logger.formatter_value(record, field_value)
            for field_name, field_value in self.fields.items()
        }

        if isinstance(record.msg, Mapping):
            message.update(record.msg)
        else:
            message[self.message_field_name] = super().formatMessage(record)

        message.update(logger.log_extra_attrs(record))
        message['msg'] = record.msg or record.message

        if record.name == 'sqlalchemy.engine.Engine':
            _no_sql = ('\n', '\t')
            for _spec in _no_sql:
                message['msg'] = str(message['msg']).replace(_spec, ' ')

        caller = Path(record.pathname)

        message['path'] = '../{parent}/{name}/{script}'.format(
            parent=caller.parent.parent.name,
            name=caller.parent.name,
            script=caller.name,
        )

        _debug = 'true' in str(os.environ.get('DEBUG', '')).lower()

        if record.exc_info:
            message['exception'] = {
                'type': record.exc_info[0].__name__,
                'msg': str(record.exc_info[1]),
            }

            if _debug:
                message['exception'].update({
                    'stack': logger.Traceback(record.exc_info[2]).as_dict(),
                })

        if len(message) == 1 and self.message_field_name in message:
            return super().formatMessage(record)

        _fmt_style = formatter_from_event_type(record.levelno)

        return term.highlight(
            json.dumps(
                message,
                default=logger.default_converter,
                indent=4,
                ensure_ascii=False,
            ),
            lexer=term.JsonLexer(),
            formatter=term.Terminal256Formatter(style=_fmt_style),
        )


class RPCFormatter(Formatter):

    """RPC Log formatter."""

    pass


__all__ = ('Formatter', 'RPCFormatter')
