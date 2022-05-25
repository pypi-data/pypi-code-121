# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api import Finding
from contrast.agent.assess.rules.base_rule import BaseRule


class BaseResponseRule(BaseRule):
    EXCLUDED_RESPONSE_CODES = [301, 302, 307, 404, 410, 500]
    EXCLUDED_CONTENT_TYPES = ["json", "xml"]

    @property
    def name(self):
        raise NotImplementedError

    def is_violated(self, header, body, form_tags, meta_tags):
        raise NotImplementedError

    def is_valid(self, status_code, content_type):
        """
        Rule is valid for analysis if response has matching content-type and status-code
        :return: bool
        """
        return not (
            status_code in self.EXCLUDED_RESPONSE_CODES
            or any(
                [
                    c_type
                    for c_type in self.EXCLUDED_CONTENT_TYPES
                    if c_type in content_type
                ]
            )
        )

    def add_events_to_finding(self, finding, **kwargs):
        # Response rules do not have events to add to a finding
        pass

    def update_preflight_hash(self, hasher, **kwargs):
        # Response rules do not update the hash
        pass

    def create_finding(self, properties):
        return Finding(self, properties)
