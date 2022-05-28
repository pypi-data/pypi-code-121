# -*- coding: utf-8 -*-
'''
subjects module for reinforcement learning
==========================================

This module provides different subjects in reinforcement learning
context.

Classes
-------
Subject:
    The base class of all `subject` classes.

SubjectDemon:
    A class that allows a `subject` to be manipulated.
'''

from .subject import Subject  # noqa: W0611
from .subject_demon import SubjectDemon, Modifier  # noqa: W0611
