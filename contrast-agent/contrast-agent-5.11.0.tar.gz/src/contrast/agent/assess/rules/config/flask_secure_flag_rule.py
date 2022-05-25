# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.config.base_flask_config_rule import (
    BaseFlaskConfigRule,
)
from .secure_flag_rule import SecureFlagRuleMixin


class FlaskSecureFlagRule(SecureFlagRuleMixin, BaseFlaskConfigRule):
    SETTINGS_VALUE = "SESSION_COOKIE_SECURE"
