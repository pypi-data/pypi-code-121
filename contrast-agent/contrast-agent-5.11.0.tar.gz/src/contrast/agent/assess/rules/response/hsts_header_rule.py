# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re
from contrast.agent.assess.rules.response.base_header_only_rule import (
    BaseHeaderOnlyRule,
)


class HstsHeaderRule(BaseHeaderOnlyRule):
    """
    Rule is violated if the header Strict-Transport-Security `max-age=` is present
    and assigned to 0.

    This is safe by default if the header isn't present.
    """

    @property
    def name(self):
        return "hsts-header-missing"

    @property
    def header_key(self):
        return "Strict-Transport-Security"

    @property
    def good_value(self):
        # unused
        pass

    @property
    def bad_value(self):
        return 0

    @property
    def good_values(self):
        # unused
        pass

    def is_header_violated(self, headers):
        value = headers.get(self.header_key)

        if value is None:
            # no finding if header is missing (safe by default)
            return False, None

        try:
            max_age_value = int(re.search(r"(?<=max-age=)\d+", value).group())
        except Exception:
            # If we know the header is there but for some reason can't process
            # the max age value, let's call it unsafe.
            properties = dict(
                type="Header",
                name=self.header_key,
                value=value,
            )
            return True, properties

        if max_age_value <= self.bad_value:
            properties = dict(
                type="Header",
                name=self.header_key,
                value=max_age_value,
            )
            return True, properties

        return False, None
