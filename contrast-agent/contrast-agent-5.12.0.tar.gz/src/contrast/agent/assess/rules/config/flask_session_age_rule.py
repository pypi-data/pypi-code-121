# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.config.base_flask_config_rule import (
    BaseFlaskConfigRule,
)
from contrast.agent.assess.rules.config.session_age_rule import SessionAgeRuleMixin


class FlaskSessionAgeRule(SessionAgeRuleMixin, BaseFlaskConfigRule):
    SETTINGS_VALUE = "PERMANENT_SESSION_LIFETIME"
