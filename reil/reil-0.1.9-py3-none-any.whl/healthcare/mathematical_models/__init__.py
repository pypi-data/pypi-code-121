# -*- coding: utf-8 -*-
'''
healthcare mathematical models module
=====================================

This module provides mathematical models, e.g. PK/PDs, cancer PDEs, etc.

Classes
-------
HealthMathModel:
    The base class for healthcare math models.

HambergPKPD:
    Hamberg's warfarin PK/PD model.
'''

from .health_math_model import HealthMathModel  # noqa: W0611
from .hamberg_pkpd import HambergPKPD  # noqa: W0611
