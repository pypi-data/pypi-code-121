# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from inspect import ismethoddescriptor, ismodule

from contrast.agent.assess.rules.static_rule import StaticRule
from contrast.agent.settings import Settings
from contrast.utils.decorators import fail_quietly
from contrast.utils.stdlib_modules import is_stdlib_module
from .code_parser_mixin import CodeParserMixin

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class HardcodedValueRule(StaticRule, CodeParserMixin):
    MODULES_TO_IGNORE = [
        "contrast",
        "django",
        "flask",
        "jinja2",
        "pyramid",
        "webob",
        "werkzeug",
    ]

    @property
    def name(self):
        return "hardcoded-value-rule"

    def applies_to(self, _):
        settings = Settings()

        return settings.is_assess_enabled() and not self.disabled

    def is_name_valid(self, constant):
        raise NotImplementedError

    def is_value_type_valid(self, constant_value):
        raise NotImplementedError

    def is_value_valid(self, value):
        return True

    @fail_quietly("Unable to analyze module")
    def analyze(self, cls_or_module):
        if self.disabled:
            return

        if self._should_ignore_module(cls_or_module):
            return

        attributes = dir(cls_or_module)

        # keep track of parsed code if it has been parsed already
        # to not parse it multiple times for the same cls_or_module
        code_ast = None
        for attribute in attributes:
            if self.is_private(attribute):
                continue

            if self.is_name_valid(attribute):
                continue

            attr_value = getattr(cls_or_module, attribute)

            if ismethoddescriptor(attr_value):
                continue

            if not self.is_value_type_valid(attr_value):
                continue

            if not self.is_value_valid(attr_value):
                continue

            hardcoded_found, code_ast = self.find_hardcoded_str(
                cls_or_module, attribute, code_ast
            )
            if not hardcoded_found:
                continue

            self.report_finding(cls_or_module, attribute)

    # The name of the field
    CONSTANT_NAME = "name"
    # The code line, recreated, with the password obfuscated
    CODE_SOURCE = "codeSource"
    # The constant name
    SOURCE = "source"

    def update_preflight_hash(self, hasher, source_name=None, constant=None, **kwargs):
        """
        Override method in base class for custom preflight hash generation
        """
        hasher.update(source_name)
        hasher.update(constant)

    def report_finding(self, cls_or_module, constant):
        if ismodule(cls_or_module):
            source = cls_or_module.__file__
            source_name = cls_or_module.__name__
            constant_name = constant
        else:
            source = sys.modules[cls_or_module.__module__].__file__
            source_name = f"{cls_or_module.__module__}.{cls_or_module.__name__}"
            constant_name = f"{cls_or_module.__name__}.{constant}"

        logger.debug("Reporting finding in %s for %s", source_name, constant)

        properties = {}
        properties[self.SOURCE] = source
        properties[self.CONSTANT_NAME] = constant
        properties[self.CODE_SOURCE] = f"{constant_name}{self.redacted_marker}"

        self.build_and_send_finding(
            properties, source_name=source_name, constant=constant
        )

    def add_events_to_finding(self, finding, **kwargs):
        # Hardcoded provider rules do not have events to add to a finding
        pass

    @property
    def redacted_marker(self):
        return " = [**REDACTED**]"

    def _should_ignore_module(self, cls_or_module):
        """
        Return True if the module (or the class's module) should be ignored.
        """
        if ismodule(cls_or_module):
            name = cls_or_module.__name__
        else:
            name = cls_or_module.__module__

        if is_stdlib_module(name):
            return True

        module_name = name.lower() + "."
        if any(module_name.startswith(item) for item in self.MODULES_TO_IGNORE):
            return True

        return False

    def is_private(self, attribute):
        """
        A class or module attribute is private if
        it's prefixed with __ or _ or  cs__
        :param attribute: str representing an attribute
        :return: bool
        """
        return (
            attribute.startswith("__")
            or attribute.startswith("_")
            or attribute.startswith("cs__")
        )

    def fuzzy_match(self, constant_value, field_names):
        lower_cont = constant_value.lower()
        return [
            lower_cont.startswith(name.lower()) or lower_cont.endswith(name.lower())
            for name in field_names
        ]
