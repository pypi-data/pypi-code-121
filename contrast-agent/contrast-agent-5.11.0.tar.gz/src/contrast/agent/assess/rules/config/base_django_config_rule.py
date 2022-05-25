# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.config.base_config_rule import BaseConfigRule
from contrast.utils.decorators import fail_quietly


class BaseDjangoConfigRule(BaseConfigRule):

    # This should be overridden by child classes
    SETTINGS_VALUE = ""

    @property
    def name(self):
        raise NotImplementedError

    def get_snippet(self, value):
        """
        Build snippet to present in TS

        Eventually we could actually parse the settings file and provide context,
        but that seems like overkill right now.
        """
        if value is None:
            return f"[{self.SETTINGS_VALUE} not defined]"
        return f"{self.SETTINGS_VALUE} = {value!r}"

    def get_config_value(self, settings):
        return getattr(settings, self.SETTINGS_VALUE, None)

    def is_violated(self, value):
        raise NotImplementedError

    @fail_quietly("Failed to apply config rule")
    def apply(self, settings, config_module):
        value = self.get_config_value(settings)
        if not self.is_violated(value):
            return

        properties = self.create_properties(value, config_module.__file__)

        self.build_and_send_finding(
            properties, settings_module_path=config_module.__file__
        )

    def update_preflight_hash(self, hasher, settings_module_path=""):
        """
        Override method in base class for custom preflight hash generation
        """
        hasher.update(settings_module_path)
