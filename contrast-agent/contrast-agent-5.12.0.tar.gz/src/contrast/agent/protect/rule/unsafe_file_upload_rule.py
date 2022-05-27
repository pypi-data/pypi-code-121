# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule


class UnsafeFileUpload(BaseRule):
    """
    Unsafe File Upload rule to protect against potentially malicious
    files that get uploaded
    """

    RULE_NAME = "unsafe-file-upload"
