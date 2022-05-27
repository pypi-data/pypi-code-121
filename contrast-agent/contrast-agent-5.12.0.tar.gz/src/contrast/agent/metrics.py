# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class MetricsDict(dict):
    def __init__(self, value_type):
        self._value_type = value_type

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            logger.debug(
                "WARNING: non-string key will be omitted from telemetry metrics",
                key=key,
                value=value,
            )
            return
        if not re.fullmatch(r"[a-zA-Z0-9\._-]{1,63}", key):
            logger.debug(
                "WARNING: invalid key will be omitted from telemetry metrics",
                key=key,
                value=value,
            )
            return
        if len(key) >= 28:
            # we enforce this condition separately from the regex in order to exactly
            # align with regex in the spec
            logger.debug(
                "WARNING: too-long key will be omitted from telemetry metrics",
                key=key,
                value=value,
            )
            return
        if not isinstance(value, self._value_type):
            logger.debug(
                "WARNING: wrong-type value will be omitted from telemetry metrics",
                key=key,
                value=value,
                expected_type=self._value_type,
            )
            return
        if self._value_type == str and len(value) == 0:
            logger.debug(
                "WARNING: blank string value will be omitted from telemetry metrics",
                key=key,
                value=value,
                expected_type=self._value_type,
            )
            return
        if self._value_type == str and len(value) > 200:
            logger.debug(
                "WARNING: too-long string value will be omitted from telemetry metrics",
                key=key,
                value=value,
            )
            return

        key = key.lower()
        super().__setitem__(key, value)
