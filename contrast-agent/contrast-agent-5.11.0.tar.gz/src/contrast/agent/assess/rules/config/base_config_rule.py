# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.settings import Settings
from contrast.agent.assess.rules.static_rule import StaticRule


class BaseConfigRule(StaticRule):
    SESSION_ID = "sessionId"
    PATH = "path"
    SNIPPET = "snippet"

    def get_snippet(self, value):
        return NotImplementedError

    def create_properties(self, value, config_path):
        settings = Settings()

        properties = {}
        properties[self.SESSION_ID] = settings.config.session_id
        properties[self.PATH] = config_path
        properties[self.SNIPPET] = self.get_snippet(value)
        return properties
