import re
from importlib import import_module
from io import StringIO
from time import time
import datetime
import decimal
import uuid

import isodate

from django.core.exceptions import ImproperlyConfigured
from django.db import router
from django.utils.timezone import now, is_aware
from django.utils.duration import duration_iso_string

from .config import settings


def get_throttling_validators(name):
    try:
        return getattr(import_module(settings.DEFAULT_THROTTLING_VALIDATORS_PATH), name)
    except (ImportError, AttributeError):
        raise ImproperlyConfigured('Throttling validator configuration {} is not defined'.format(name))


def remove_nul_from_string(value):
    return value.replace('\x00', '')


def is_atty_string(s):
    return bool(re.search(r'^' + re.escape('\x1b[') + r'\d+m$', s))


class LogStringIO(StringIO):

    BOLD = '\x1b[1m'
    RESET = '\x1b[0m'

    def __init__(self, flush_callback=None, flush_timeout=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_closed = False
        self._last_newline = 0
        self._flush_callback = flush_callback
        self._write_time = True
        self._last_flush_time = time()
        self._flush_timeout = settings.LOG_STRING_IO_FLUSH_TIMEOUT if flush_timeout is None else flush_timeout
        self._flushed = True

    def _flush(self, force=False):
        if (not self._flushed and self._flush_callback
                and (force or time() - self._last_flush_time > self._flush_timeout)):
            self._flush_callback(self)
            self._last_flush_time = time()
            self._flushed = True

    def write(self, s):
        if not self._is_closed:
            self._flushed = False
            lines = s.split('\n')

            for i, line in enumerate(lines):
                cursor_first = True
                for cursor_block in line.split('\r'):
                    if not cursor_first:
                        self.seek(self._last_newline)
                        self.truncate()
                        self._write_time = True
                    cursor_first = False

                    if self._write_time and not is_atty_string(cursor_block):
                        cursor_block = '{}{}[{}]{} {}'.format(
                            self.RESET, self.BOLD, now().strftime('%d-%m-%Y %H:%M:%S'), self.RESET, cursor_block
                        )
                        self._write_time = False

                    super().write(cursor_block)

                if i != len(lines) - 1:
                    super().write('\n')
                    self._last_newline = self.tell()
                    self._write_time = True

            self._flush()

    def isatty(self):
        return True

    def close(self):
        self._is_closed = True
        self._flush(force=True)
        super().close()


class TeeStringIO:
    """
    StringIO that additionally writes to another stream(s).
    """
    ANSI_ESCAPE_REGEX = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def __init__(self, out, log_stream):
        self._out = out
        self._log_stream = log_stream
        self._last_newline = 0
        super().__init__()

    def write(self, s):
        if self.isatty():
            self._out.write(s)
        else:
            self._out.write(self.ANSI_ESCAPE_REGEX.sub('', s))
        self._log_stream.write(s)

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def flush(self):
        self._out.flush()
        self._log_stream.flush()


def regex_sub_groups_global(pattern, repl, string):
    """
    Globally replace all groups inside pattern with `repl`.
    If `pattern` doesn't have groups the whole match is replaced.
    """
    for search in reversed(list(re.finditer(pattern, string))):
        for i in range(len(search.groups()), 0 if search.groups() else -1, -1):
            start, end = search.span(i)
            string = string[:start] + repl + string[end:]
    return string


def update_logged_request_data(request, related_objects=None, slug=None, extra_data=None):
    input_request_logger = getattr(request, 'input_request_logger', None)
    if input_request_logger:
        if related_objects:
            input_request_logger.add_related_objects(*related_objects)
        if slug:
            input_request_logger.set_slug(slug)
        if extra_data:
            input_request_logger.update_extra_data(extra_data)


def get_object_triple(obj):
    from django.contrib.contenttypes.models import ContentType

    if isinstance(obj, (list, tuple)) and len(obj) == 3:
        return tuple(obj)
    else:
        content_type = ContentType.objects.get_for_model(obj)
        return router.db_for_write(content_type.model_class()), content_type.pk, obj.pk


def serialize_data(o):
    if isinstance(o, datetime.datetime):
        r = o.isoformat()
        if o.microsecond:
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'
        return {'@type': 'datetime',  '@value': r}
    elif isinstance(o, datetime.date):
        return {'@type': 'date',  '@value': o.isoformat()}
    elif isinstance(o, datetime.time):
        if is_aware(o):
            raise ValueError("JSON can't represent timezone-aware times.")
        r = o.isoformat()
        if o.microsecond:
            r = r[:12]
        return {'@type': 'time', '@value': r}
    elif isinstance(o, datetime.timedelta):
        return {'@type': 'timedelta', '@value': duration_iso_string(o)}
    elif isinstance(o, decimal.Decimal):
        return {'@type': 'decimal', '@value': str(o)}
    elif isinstance(o, uuid.UUID):
        return {'@type': 'uuid', '@value': str(o)}
    elif isinstance(o, (list, tuple, set)):
        return [serialize_data(v) for v in o]
    elif isinstance(o, dict):
        return {
            k: serialize_data(v) for k, v in o.items()
        }
    else:
        return o


def deserialize_data(o):
    if isinstance(o, dict) and set(o.keys()) == {'@type', '@value'}:
        o_type, o_value = o['@type'], o['@value']
        if o_type == 'uuid':
            return uuid.UUID(o_value)
        elif o_type == 'decimal':
            return decimal.Decimal(o_value)
        elif o_type == 'timedelta':
            return isodate.parse_duration(o_value)
        elif o_type == 'time':
            return isodate.parse_time(o_value)
        elif o_type == 'date':
            return isodate.parse_date(o_value)
        elif o_type == 'datetime':
            return isodate.parse_datetime(o_value)
    elif isinstance(o, dict):
        return {
            k: deserialize_data(v) for k, v in o.items()
        }
    elif isinstance(o, list):
        return [deserialize_data(v) for v in o]
    else:
        return o
