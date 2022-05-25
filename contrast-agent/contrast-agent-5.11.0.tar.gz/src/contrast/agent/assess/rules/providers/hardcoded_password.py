# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.agent.assess.rules.providers.hardcoded_value_rule import (
    HardcodedValueRule,
)
from contrast.utils.string_utils import ensure_string


class HardcodedPassword(HardcodedValueRule):
    """
    Determine if there are any passwords hardcoded into the sourcecode
    of the application. A constant is a password if:
    1) the name contains a PASSWORD_FIELD_NAMES value
    2) the name does not contain a NON_PASSWORD_PARTIAL_NAMES value
    3) the value is a String
    4) the value is not solely alphanumeric and '.' or '_' * note that mixing the
       characters counts as a violation of this rule
    """

    @property
    def name(self):
        return "hardcoded-password"

    # These are names, determined by the security team (Matt & Ar), that
    # indicate a field is likely to be a password or secret token of some
    # sort.
    PASSWORD_FIELD_NAMES = ["PASSWORD", "PASSKEY", "PASSPHRASE", "SECRET"]

    # These are markers whose presence indicates that a field is more
    # likely to be a descriptor or requirement than an actual password.
    # We should ignore fields that contain them.
    NON_PASSWORD_PARTIAL_NAMES = [
        "DATE",
        "FORGOT",
        "FORM",
        "ENCODE",
        "PATTERN",
        "PREFIX",
        "PROP",
        "SUFFIX",
        "URL",
        "BASE",
        "FILE",
    ]

    def is_name_valid(self, constant):
        not_in_password_fields = not any(
            self.fuzzy_match(constant, self.PASSWORD_FIELD_NAMES)
        )
        in_partial_names = any(
            self.fuzzy_match(constant, self.NON_PASSWORD_PARTIAL_NAMES)
        )
        return not_in_password_fields or in_partial_names

    def is_value_valid(self, value):
        return not self.probably_property_name(value)

    def is_value_type_valid(self, value):
        return isinstance(value, (bytes, str, bytearray))

    # If a field name matches an expected password field, we'll check it's
    # value to see if it looks like a placeholder. For our purposes,
    # placeholders will be any non-empty String conforming to the patterns
    # below.
    PROPERTY_NAME_PATTERN = re.compile("^[a-z]+[._][._a-z]*[a-z]+$")

    def probably_property_name(self, value):
        return re.match(self.PROPERTY_NAME_PATTERN, ensure_string(value)) is not None
