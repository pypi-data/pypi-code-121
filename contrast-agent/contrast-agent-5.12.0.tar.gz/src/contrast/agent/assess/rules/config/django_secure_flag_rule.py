# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.rules.config.base_django_config_rule import (
    BaseDjangoConfigRule,
)
from .secure_flag_rule import SecureFlagRuleMixin


class DjangoSecureFlagRule(SecureFlagRuleMixin, BaseDjangoConfigRule):
    SETTINGS_VALUE = "SESSION_COOKIE_SECURE"
