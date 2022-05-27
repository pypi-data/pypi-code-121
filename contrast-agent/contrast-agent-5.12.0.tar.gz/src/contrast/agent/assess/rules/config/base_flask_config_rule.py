# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.agent.assess.rules.config.base_config_rule import BaseConfigRule
from contrast.utils.decorators import fail_quietly


class BaseFlaskConfigRule(BaseConfigRule):

    # This should be overridden by child classes
    SETTINGS_VALUE = ""

    @property
    def name(self):
        raise NotImplementedError

    def get_config_value(self, config):
        return config.get(self.SETTINGS_VALUE)

    def is_violated(self, value):
        raise NotImplementedError

    def get_path(self, app):
        app_module = sys.modules.get(app.name)
        if not app_module:
            return ""

        return app_module.__file__

    def get_snippet(self, value):
        return f'app.config["{self.SETTINGS_VALUE}"] = {value!r}'

    @fail_quietly("Failed to apply config rule")
    def apply(self, app):
        value = self.get_config_value(app.config)
        if not self.is_violated(value):
            return

        config_path = self.get_path(app)

        properties = self.create_properties(value, config_path)

        self.build_and_send_finding(
            properties, settings_module_path=(config_path or app.name)
        )

    def update_preflight_hash(self, hasher, settings_module_path=""):
        """
        Override method in base class for custom preflight hash generation
        """
        hasher.update(settings_module_path)
