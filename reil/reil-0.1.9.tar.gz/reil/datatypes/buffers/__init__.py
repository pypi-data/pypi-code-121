# -*- coding: utf-8 -*-
'''
Buffers module for reinforcement learning
==========================================

This module provides different types of buffer.

Classes
-------
Buffer:
    Base class for all buffers. It provides basic functionality for setup,
    adding to and picking from the buffer.

CircularBuffer:
    A buffer that overwrites the oldest items if more than its size
    is added.

EndlessBuffer:
    A buffer without an end! This buffer keeps appending new items,
    so it should be used with memory and performance constraints in mind.

VanilaExperienceReplay:
    A `CircularBuffer` that only picks randomly and returns
    values only if it is full.


'''

from .buffer import Buffer, PickModes  # noqa: W0611
from .circular_buffer import CircularBuffer  # noqa: W0611
from .endless_buffer import EndlessBuffer  # noqa: W0611
from .sink import Sink  # noqa: W0611
from .vanilla_experience_replay import VanillaExperienceReplay  # noqa: W0611
