# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.settings import Settings
from contrast.utils.digest_utils import Digest
from contrast.utils.timer import now_ms
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class BaseRule(object):
    """
    Base rule object that all assess rules will inherit
    """

    def __init__(self):
        self.findings_per_agent_run = 0

    @property
    def name(self):
        raise NotImplementedError

    @property
    def disabled(self):
        """
        Property indicating whether rule is disabled
        """
        return Settings().is_assess_rule_disabled(self.name)

    def finding_reported(self):
        self.findings_per_agent_run += 1

    def add_events_to_finding(self, finding, events=None, **kwargs):
        if events is not None:
            finding.events.extend(events)

    def generate_preflight_hash(self, **kwargs):
        hasher = Digest()
        hasher.update(self.name)

        self.update_preflight_hash(hasher, **kwargs)

        return hasher.finish()

    def update_preflight_hash(self, hasher, **kwargs):
        """
        Update preflight hash with additional rule-specific data

        Child classes should override this method in order to customize the
        kind of data that is used to generate the preflight hash.

        @param hasher: Hash class to be updated with additional data
        @param **kwargs: Placeholder for keyword args used by child classes
        """
        raise NotImplementedError

    def count_threshold_reached(self):
        """
        Use the configurable max vulnerability threshold and agent runtime window
        to determine if we've already created the maximum number of
        vulnerabilities for this rule.

        RACE CONDITION:  a possible race condition can happen of multiple threads
        check this method. The outcome is relatively low risk - worst case we will
        end up making more vulnerabilities than the threshold.
        """
        settings = Settings()
        result = True

        if self.findings_per_agent_run + 1 <= settings.max_vulnerability_count:
            result = False
        else:
            logger.warning(
                "%s vulnerability will not be reported. %s vulnerabilities already reported",
                self.name,
                self.findings_per_agent_run,
            )

        if now_ms() - settings.agent_runtime_window >= settings.agent_runtime_threshold:
            self.findings_per_agent_run = 0
            settings.agent_runtime_window = now_ms()

        return result
