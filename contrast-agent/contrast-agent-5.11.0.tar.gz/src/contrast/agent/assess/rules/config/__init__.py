# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from .django_httponly_rule import DjangoHttpOnlyRule
from .django_session_age_rule import DjangoSessionAgeRule
from .django_secure_flag_rule import DjangoSecureFlagRule
from .flask_httponly_rule import FlaskHttpOnlyRule
from .flask_session_age_rule import FlaskSessionAgeRule
from .flask_secure_flag_rule import FlaskSecureFlagRule
