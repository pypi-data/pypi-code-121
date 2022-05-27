# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_header_only_rule import (
    BaseHeaderOnlyRule,
)


class XXssProtectionDisabledRule(BaseHeaderOnlyRule):
    """
    Rule is violated if the X-XSS-Protection header is present and disables XSS
    protection. This is safe by default if the header isn't present.
    """

    @property
    def name(self):
        return "xxssprotection-header-disabled"

    @property
    def header_key(self):
        return "X-XSS-Protection"

    @property
    def good_value(self):
        return "1"

    @property
    def good_values(self):
        # unused
        pass

    def is_header_violated(self, headers):
        value = headers.get(self.header_key)
        if value is None:
            # no finding if header is missing (safe by default)
            return False, None

        if not value.startswith(self.good_value):
            properties = dict(
                type="Header",
                name=self.header_key,
                value=value,
            )
            return True, properties

        return False, None
