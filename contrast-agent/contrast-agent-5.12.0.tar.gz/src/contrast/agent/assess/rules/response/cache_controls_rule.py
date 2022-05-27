# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_response_rule import BaseResponseRule
from contrast.api import Finding


class CacheControlsRule(BaseResponseRule):
    GOOD_VALUES = ("no-cache", "no-store")

    @property
    def name(self):
        return "cache-controls-missing"

    def is_violated(self, headers, _, form_tags, meta_tags):
        header_violated, header_properties = self.is_header_violated(headers)
        if not header_violated:
            # If header is correctly configured for this rule, no need to check body.
            return False, {}

        body_violated, body_properties = self.is_body_violated(meta_tags)
        if not body_violated:
            # Even though header may have violated the rule, if the body was configured
            # correctly for this rule, the rule is not violated.
            return False, {}

        return True, header_properties or body_properties

    def is_header_violated(self, headers):
        """
        Rule is violated if Cache-Control header is present OR it is present
        but not assigned to a desired value.
        :param headers: dict of response headers
        :return: (bool, properties)
        """
        value = headers.get("Cache-Control")
        if not value:
            # Finding gets no properties if header is missing
            return True, {}

        if value not in self.GOOD_VALUES:
            properties = dict(
                type="Header",
                name="Cache-Control",
                value=value,
            )
            return True, properties

        return False, None

    def is_body_violated(self, meta_tags):
        """
        Rule is violated if:
        1. none of the attrs of the list of form tags have an "autocomplete" attr
        2. at least one attr is "autocomplete" but it is is assigned to anything other than "off"
        :param body: response body
        :param form_tags: list of Tag namedtuple
        :return: bool, properties dict
        """
        if not meta_tags:
            return True, {}

        first_relevant_tag = None
        for tag in meta_tags:
            for attr_idx, (attr_name, attr_value) in enumerate(tag.attrs):

                if (
                    attr_name.lower() == "http-equiv"
                    and attr_value.lower() == "cache-control"
                ):
                    first_relevant_tag = tag
                    content, value = tag.attrs[attr_idx + 1]
                    if (
                        content.lower() == "content"
                        and value.lower() in self.GOOD_VALUES
                    ):
                        return False, {}

        # If no cache-control attr in any meta tag, report the first meta tag since
        # they are all in violation.
        properties = self.build_properties(first_relevant_tag)
        return True, properties

    def build_properties(self, tag):
        if not tag:
            return dict()
        return dict(
            type=tag.type,
            name="pragma",
            value=tag.tag,
        )

    def create_finding(self, properties):
        if not properties:
            data = dict(data="[]")
        else:
            data = dict(data=f"[{str(properties)}]")
        return Finding(self, data)
