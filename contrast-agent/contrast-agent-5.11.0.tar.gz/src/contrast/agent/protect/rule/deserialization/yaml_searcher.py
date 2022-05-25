# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re
from contrast.agent.protect.rule.deserialization.custom_searcher import CustomSearcher
from contrast.utils.pattern_builder import PatternBuilder


class YAMLSearcher(CustomSearcher):
    ID = "UD-YAML-1"

    PYTHON_TAG = "!!python"

    def __init__(self):
        CustomSearcher.__init__(self, self.ID)

    @property
    def pattern(self):
        # !!(str|null|int|bool|float|binary|timestamp|omap|pairs|set|seq|map|python)

        return (
            PatternBuilder()
            .literally("!!")
            .any_of_these(
                [
                    "str",
                    "null",
                    "int",
                    "bool",
                    "float",
                    "binary",
                    "timestamp",
                    "omap",
                    "pairs",
                    "set",
                    "seq",
                    "map",
                    "python/name",
                    "python/module",
                    "python/object/new",
                    "python/object/apply",
                ]
            )
            .build()
        )

    def impact_of(self, value):
        count = 0
        impact = self.IMPACT_NONE

        matches = re.finditer(self.pattern, value)

        for match in matches:
            count += 1

            if match.group(0).startswith(self.PYTHON_TAG):
                return self.IMPACT_CRITICAL

        if count > 2:
            impact = self.IMPACT_MEDIUM
        elif count >= 1:
            impact = self.IMPACT_LOW

        return impact
