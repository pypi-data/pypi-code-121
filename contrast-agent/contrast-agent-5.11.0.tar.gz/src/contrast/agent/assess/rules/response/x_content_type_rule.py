# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_header_only_rule import (
    BaseHeaderOnlyRule,
)


class XContentTypeRule(BaseHeaderOnlyRule):
    """
    Rule is violated if the header X-Content-Type-Options is missing or present
    but not assigned to a desired value.
    """

    @property
    def name(self):
        return "xcontenttype-header-missing"

    @property
    def header_key(self):
        return "X-Content-Type-Options"

    @property
    def good_values(self):
        return ("nosniff",)
