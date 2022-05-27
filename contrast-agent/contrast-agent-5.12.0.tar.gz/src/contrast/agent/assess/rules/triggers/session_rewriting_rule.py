# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.triggers.trigger_config_rule import TriggerConfigRule


class SessionRewritingRule(TriggerConfigRule):
    @property
    def name(self):
        return "session-rewriting"

    def is_violated(self, node, source, **kwargs):
        """
        The rule is violated if the value is False or if it is not set at all (None)
        """
        if self.count_threshold_reached():
            return False
        return not source

    def is_violated_properties(*args, **kwargs):
        """Override for safety. In theory, this should never be called."""
        return False
