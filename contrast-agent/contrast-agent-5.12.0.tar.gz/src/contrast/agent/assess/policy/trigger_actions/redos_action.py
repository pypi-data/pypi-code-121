# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re
from contrast.agent.assess.policy.trigger_actions.default_action import DefaultAction
from contrast.utils.decorators import fail_quietly

# Used to determine if the input violates the constraint in the
# specification linked above, meaning it has two or more layers of nested
# multi-match groups.
REDOS_REGEX_STRING = r"[\[(].*?[\[(].*?[\])][*+?].*?[\])][*+?]"
# For matching bytes and bytearray objects
REDOS_REGEX_BYTES = REDOS_REGEX_STRING.encode()


# re pattern type varies across Py versions and some even have bugs
# https://github.com/beetbox/beets/issues/2986
# So while this looks hacky, it will work.
PATTERN_TYPE = type(re.compile(""))


class RedosAction(DefaultAction):
    """
    Custom trigger action that implements ReDos rule logic.

    A ReDOS vulnerability is triggered when the user input is untrusted (as
    with other rules) but unlike other rules, when the regex passed in to the re
    method matches a specific pattern. This rule deviates from other Assess rules in
    that the value provided may change the outcome of the vulnerability detection.

    https://bitbucket.org/contrastsecurity/assess-specifications/src/master/rules/dataflow/redos.md
    """

    def is_violated(
        self, source_properties, required_tags, disallowed_tags, orig_args=None
    ):
        # 1) Check that user input is untrusted.
        violated = super().is_violated(
            source_properties, required_tags, disallowed_tags
        )
        if not violated:
            return False

        # 2) check that regex passed in to re method matches our ReDOs regex.
        return self._is_complex_regex(orig_args)

    @fail_quietly("Failed check regex complexity", return_value=False)
    def _is_complex_regex(self, orig_args):
        if not orig_args:
            return False

        # orig_args is (regex, user_string)
        regex = orig_args[0]

        if isinstance(regex, PATTERN_TYPE):
            regex = regex.pattern

        redos_regex = (
            REDOS_REGEX_STRING if isinstance(regex, str) else REDOS_REGEX_BYTES
        )

        # Even though Ruby uses `match`, we have to use `search` which checks for
        # a match anywhere in the string, not just the beginning.
        return bool(re.search(redos_regex, regex, flags=re.IGNORECASE))
