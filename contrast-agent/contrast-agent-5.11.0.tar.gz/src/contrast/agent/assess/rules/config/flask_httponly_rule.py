# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.config.base_flask_config_rule import (
    BaseFlaskConfigRule,
)
from .httponly_rule import HttpOnlyRuleMixin


class FlaskHttpOnlyRule(HttpOnlyRuleMixin, BaseFlaskConfigRule):
    SETTINGS_VALUE = "SESSION_COOKIE_HTTPONLY"
