# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.utils.command_scanner import CommandScanner
from contrast.utils.decorators import cached_property


class CommandInjectionREPMixin(object):
    REP_DETECT_PARAMETER_COMMAND_BACKDOORS = "detect_parameter_command_backdoors"
    REP_DETECT_PARAMETER_COMMAND_BACKDOORS_ID = "REP_DETECT_PARAMETER_COMMAND_BACKDOORS"

    REP_DETECT_CHAINED_COMMANDS = "detect_chained_commands"

    @cached_property
    def is_detect_parameter_command_backdoors_enabled(self):
        return self.settings.is_rep_feature_enabled_for_rule(
            self.name, self.REP_DETECT_PARAMETER_COMMAND_BACKDOORS
        )

    @cached_property
    def is_detect_chained_commands_enabled(self):
        return self.settings.is_rep_feature_enabled_for_rule(
            self.name, self.REP_DETECT_CHAINED_COMMANDS
        )

    def get_first_command_chain_index(self, command):
        parsed_results = CommandScanner.parse(command)
        chain_indices = parsed_results.command_chains

        return chain_indices[0] if chain_indices else -1
