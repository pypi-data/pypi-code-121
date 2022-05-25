# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.providers.hardcoded_value_rule import (
    HardcodedValueRule,
)


class HardcodedKey(HardcodedValueRule):
    # These are names, determined by the security team, that indicate a field
    # is likely to be a password or secret token of some sort.
    KEY_FIELD_NAMES = ["KEY", "AES", "DES", "IV", "SECRET"]

    # These are markers whose presence indicates that a field is more
    # likely to be a descriptor or requirement than an actual key.
    # We should ignore fields that contain them.
    NON_KEY_NAMES = ["CONTENT_CODES", "RESPONSE_CODES", "DIV"]

    @property
    def name(self):
        return "hardcoded-key"

    def is_name_valid(self, contant):
        name_in_key_fields = not any(self.fuzzy_match(contant, self.KEY_FIELD_NAMES))
        return name_in_key_fields or contant in self.NON_KEY_NAMES

    def is_value_type_valid(self, value):
        """
        A value has a value type if it it a str or bytes
        """
        if not value:
            return False

        return isinstance(value, (bytes, str, bytearray))
