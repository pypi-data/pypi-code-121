# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import platform
import sys

from datetime import datetime, timezone

import contrast
from contrast.extern import structlog as logging
from contrast.agent.exceptions import _Exception
from contrast.agent.validator import Validator
from contrast.agent.metrics import MetricsDict
from contrast import __version__

logger = logging.getLogger("contrast")


class TelemetryEvent(object):
    def __init__(self):

        self.timestamp = datetime.now(timezone.utc).astimezone().isoformat()
        self.telemetry_instance_id = contrast.TELEMETRY.instance_id
        self.tags = MetricsDict(str)

    @property
    def path(self):
        return ""

    def add_tags(self):
        telemetry = contrast.TELEMETRY
        settings = telemetry.settings

        self.tags["is_public_build"] = str(telemetry.is_public_build).lower()
        self.tags["agent_version"] = __version__
        self.tags["python_version"] = sys.version
        self.tags["python_version_simple"] = platform.python_version()
        self.tags["os_type"] = platform.system()
        self.tags["os_arch"] = platform.machine()
        self.tags["os_version"] = platform.version()
        self.tags["app_framework_version"] = str(settings.framework)
        self.tags["server_framework_version"] = str(settings.server)
        self.tags["teamserver"] = settings.config.teamserver_type

        if settings.rewriter_enabled:
            self.tags["rewriter_enabled"] = "true"

    def to_json(self):
        return dict(
            timestamp=self.timestamp,
            instance=self.telemetry_instance_id,
            tags=self.tags,
        )


class MetricsTelemetryEvent(TelemetryEvent):
    def __init__(self):
        super().__init__()
        self.fields = MetricsDict(int)
        self.fields["_filler"] = 0

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.to_json()}"

    def to_json(self):
        return {
            **super().to_json(),
            **dict(fields=self.fields),
        }


class StartupMetricsTelemetryEvent(MetricsTelemetryEvent):
    def __init__(self):
        super().__init__()

        try:
            self.add_tags()
        except Exception as ex:
            logger.debug("Telemetry failed to create StartupMetrics msg: %s", ex)
            logger.debug("Disabling telemetry")
            contrast.TELEMETRY.enabled = False

    @property
    def path(self):
        return "/metrics/startup"


class ErrorTelemetryEvent(TelemetryEvent, Validator):
    VALIDATIONS = dict(
        telemetry_instance_id=dict(required=True, range=(12, 64)),
        # tags field is required to be reported but can be empty
        tags=dict(required=True, range=(0, 512)),
        exceptions=dict(required=True, range=(1, 512)),
        # some agents use this for named logger
        logger=dict(required=False, range=(0, 128)),
        # logged message, not exception message
        message=dict(required=False, range=(0, 256)),
        occurrences=dict(required=False, default=0),
    )

    def __init__(self, error: Exception, logger_="", message=""):
        super().__init__()

        # We may not use this field, it's meant to represent a named logger
        # to easily filter a specific feature
        self.logger = logger_
        # message that was logged, not the exception message
        self.message = message
        self.occurrences = 1
        self.exceptions = [_Exception(error)]

        try:
            self.add_tags()
        except Exception as ex:
            logger.debug("Adding tags failed: %s", ex)

        self.validate()

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.to_json()}"

    @property
    def path(self):
        return "/exceptions/error"

    def to_json(self):
        return {
            **super().to_json(),
            **dict(
                occurrences=self.occurrences,
                logger=self.logger,
                message=self.message,
                exceptions=[ex.to_json() for ex in self.exceptions],
            ),
        }
