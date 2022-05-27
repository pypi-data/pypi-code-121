# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_header_only_rule import (
    BaseHeaderOnlyRule,
)


class CspHeaderMissingRule(BaseHeaderOnlyRule):
    """
    Rule is violated if all the following headers:

    - Content-Security-Policy
    - X-Content-Security-Policy
    - X-Webkit-CSP

    are missing.
    """

    @property
    def name(self):
        return "csp-header-missing"

    @property
    def header_key(self):
        """We care about multiple headers for this rule, see `header_keys`"""
        pass

    @property
    def header_keys(self):
        return ("Content-Security-Policy", "X-Content-Security-Policy", "X-Webkit-CSP")

    @property
    def good_values(self):
        """We don't care about the values for this rule, only header(s) presence"""
        pass

    def is_header_violated(self, headers):
        for key in self.header_keys:
            value = headers.get(key)
            if value:
                # As long as one of the headers is present,  rule is not violated.
                return False, None

        # Finding gets no properties if header(s) is missing
        return True, {}
