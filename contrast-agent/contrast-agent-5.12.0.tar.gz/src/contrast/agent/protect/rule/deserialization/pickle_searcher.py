# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.deserialization.custom_searcher import CustomSearcher


class PickleSearcher(CustomSearcher):
    ID = "UD-PICKLE-1"

    NEW_LINE = "\n"
    ESCAPED_NEW_LINE = "\\n"

    def __init__(self):
        CustomSearcher.__init__(self, self.ID)

    def impact_of(self, value):
        impact = self.IMPACT_NONE

        split_char = (
            self.ESCAPED_NEW_LINE if self.ESCAPED_NEW_LINE in value else self.NEW_LINE
        )
        stack_commands = value.split(split_char)
        count = 0

        for command in stack_commands:
            contains_command = any(m in command for m in self.MODULES)

            if contains_command:
                count += 1

                # pushing module only the stack
                if command.startswith("c"):
                    count += 1

        if count >= 3:
            impact = self.IMPACT_CRITICAL
        elif count >= 2:
            impact = self.IMPACT_HIGH

        return impact

    MODULES = [
        "os",
        "system",
        "sys",
        "subprocess",
        "__builtin__",
        "builtins",
        "globals",
        "open",
        "popen",
    ]
