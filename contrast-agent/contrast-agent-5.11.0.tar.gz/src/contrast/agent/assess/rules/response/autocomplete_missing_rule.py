# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_body_only_rule import BaseBodyOnlyRule


class AutocompleteMissingRule(BaseBodyOnlyRule):
    @property
    def name(self):
        return "autocomplete-missing"

    def is_body_violated(self, body, form_tags):
        """
        Rule is violated if:
        1. none of the attrs of the list of form tags have an "autocomplete" attr
        2. at least one attr is "autocomplete" but it is is assigned to anything other than "off"
        :param body: response body
        :param form_tags: list of Tag namedtuple
        :return: bool, properties dict
        """
        if not form_tags:
            return False, {}

        for tag in form_tags:
            for attr_name, attr_value in tag.attrs:
                if attr_name.lower() == "autocomplete" and attr_value.lower() == "off":
                    return False, {}

        # If no autocomplete attr in any form tag, report the first form tag since
        # they are all in violation.
        properties = self.build_properties(form_tags[0].tag, body)
        return True, properties
