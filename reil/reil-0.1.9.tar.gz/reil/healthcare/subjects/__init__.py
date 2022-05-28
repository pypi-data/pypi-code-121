# -*- coding: utf-8 -*-
'''
healthcare subjects module for reinforcement learning
=====================================================

This module provides different healthcare subjects in reinforcement learning
context.

Classes
-------
HealthSubject:
    A base `Subject` that accepts a `Patient`, administers the doses,
    and record the measurement of the outcome.

Warfarin:
    A `Subject` for warfarin that uses `PatientWarfarinRavvaz` and
    `healthcare.hamberg_pkpd`.
'''

from .health_subject import HealthSubject  # noqa: W0611
from .warfarin import Warfarin  # noqa: W0611
