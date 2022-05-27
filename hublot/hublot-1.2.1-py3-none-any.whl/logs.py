#!/usr/bin/env python3

# standards
from dataclasses import dataclass
import logging
from typing import Optional, Union

# 3rd parties
from requests import PreparedRequest


LOGGER = logging.getLogger('hublot')


@dataclass(frozen=False)
class LogEntry:
    preq: PreparedRequest
    is_redirect: bool = False
    cache_key_str: Optional[str] = None
    cached: Optional[bool] = None
    courtesy_seconds: Optional[float] = None

    def _compose_line(self):
        if self.cache_key_str:
            yield f'[{self.cache_key_str}] '
        if self.cached:
            yield '[cached] '
        elif self.courtesy_seconds and self.courtesy_seconds > 0.5:
            rounded = f'{round(self.courtesy_seconds)}s'
            yield f'[{rounded:^6s}] '
        else:
            yield '         '
        if self.is_redirect:
            yield '-> '
        pr = self.preq
        yield pr.url
        if pr.method != 'GET':
            yield f' [{pr.method}'
            try:
                length = int(pr.headers.get('Content-Length', 0))
            except ValueError:
                length = 0
            if length > 0:
                yield f' {length} bytes'
            yield ']'

    def __str__(self):
        return ''.join(self._compose_line())


def basic_logging_config(level: Union[int, str] = 'INFO', propagate: bool = False):
    """
    Sets up logging for the common use case. Calls `logging.basicConfig`, lowers verbosity for the `urllib3` logger. If `propagate`
    is False (the default), a new handler will be attached to `hublot.LOGGER` that logs in a simple format to stderr, and does not
    propagate log events to the root logger.
    """
    if not isinstance(level, int):
        level = getattr(logging, level)
    logging.basicConfig(level=level)
    logging.getLogger('urllib3').setLevel(max(logging.WARNING, level))
    if not propagate and not LOGGER.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s', None, '%')
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)
        LOGGER.propagate = False
