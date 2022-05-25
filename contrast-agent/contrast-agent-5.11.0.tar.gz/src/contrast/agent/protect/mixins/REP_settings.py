# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class SettingsREPMixin(object):
    valid_rep_features = {
        "cmd-injection": [
            "detect_parameter_command_backdoors",
            "detect_chained_commands",
        ],
        "path-traversal": [
            "detect_custom_code_accessing_system_files",
            "detect_common_file_exploits",
        ],
        "sql-injection": [
            "detect_tautologies",
            "detect_dangerous_functions",
            "detect_chained_queries",
            "detect_suspicious_unions",
        ],
        "malformed-header": ["mode"],
    }

    def is_rep_feature_enabled_for_rule(self, rule_name, feature):
        rep_feature = ".".join(["protect", "rules", rule_name, feature])
        return self.config.get(rep_feature, True)

    @staticmethod
    def is_valid_rep_feature_for_rule(rule_name, key):
        if not key or not rule_name:
            return False
        return key in SettingsREPMixin.valid_rep_features[rule_name]

    @staticmethod
    def is_valid_value_for_rep_feature(value):
        return isinstance(value, bool)
