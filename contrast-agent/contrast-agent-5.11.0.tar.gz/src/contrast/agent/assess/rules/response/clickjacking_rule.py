# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_header_only_rule import (
    BaseHeaderOnlyRule,
)


class ClickjackingRule(BaseHeaderOnlyRule):
    """
    Rule is violated if the header X-Frame-Options is missing or present
    but not assigned to a desired value.
    """

    @property
    def name(self):
        return "clickjacking-control-missing"

    @property
    def header_key(self):
        return "X-Frame-Options"

    @property
    def good_values(self):
        return ("deny", "sameorigin")
