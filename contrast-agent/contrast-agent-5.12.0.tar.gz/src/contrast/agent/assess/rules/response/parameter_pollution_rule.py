# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.response.base_body_only_rule import BaseBodyOnlyRule


class ParameterPollutionRule(BaseBodyOnlyRule):
    @property
    def name(self):
        return "parameter-pollution"

    def is_body_violated(self, body, form_tags):
        """
        Rule is violated if:
        1. action attribute is missing within the form tag
        2. action attribute is unset or empty
        :param body: response body
        :param form_tags: list of Tag namedtuple
        :return: bool, properties dict
        """
        if not form_tags:
            return False, {}

        for tag in form_tags:
            action_attr_found = False

            for attr_name, attr_value in tag.attrs:
                if attr_name.lower() == "action":
                    action_attr_found = True

                    if not attr_value or attr_value.isspace():
                        properties = self.build_properties(tag.tag, body)
                        return True, properties

                    break

            if not action_attr_found:
                properties = self.build_properties(tag.tag, body)
                return True, properties

        return False, {}
