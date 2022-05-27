# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule
from contrast.api.settings_pb2 import ProtectionRule


class Xss(BaseRule):
    """
    Cross Site Scripting Protection rule
    Currently only a prefilter / block at perimeter rule
    """

    RULE_NAME = "reflected-xss"

    @property
    def mode(self):
        """
        Always block at perimeter
        """
        mode = self.mode_from_settings()

        return (
            mode
            if mode in [ProtectionRule.NO_ACTION, ProtectionRule.MONITOR]
            else ProtectionRule.BLOCK_AT_PERIMETER
        )

    def sample_dtm_to_json(self, sample):
        return {
            "input": sample.xss.input,
            "matches": [
                {
                    "evidenceStart": match.evidence_start_ms,
                    "evidence": match.evidence,
                    "offset": match.offset,
                }
                for match in sample.xss.matches
            ],
        }
