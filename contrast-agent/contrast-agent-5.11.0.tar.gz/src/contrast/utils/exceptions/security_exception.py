# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class SecurityException(Exception):

    STATUS_CODE = 403
    REASON_PHRASE = "Forbidden"
    STATUS = f"{STATUS_CODE} {REASON_PHRASE}"

    def __init__(self, rule, message=None):
        message = message if message else f"Rule {rule.name} threw a security exception"
        super(SecurityException, self).__init__(message)
