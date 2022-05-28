# -*- coding: utf-8 -*-
'''
legacy classes for reinforcement learning
=========================================

This module provides classes that are no longer supported.

Classes
-------
Environment:
    The base class that provides minimum required
    functionality for a reinforcement learning environment.

Experiment:
    An environment to explore performance of trained
    agents on subjects.

IterableSubject:
    Now `InstanceGenerator` does the job and goes beyond that!

LegacyReilData

Risk

Snake

WarfarinClusterAgent:
    an agent whose actions are based on clustering of observations.
    Note: This agent will no longer run due to changes in the module
    implementation.


MNKGame:
    A simple game consisting of an m-by-n board.
    Each player should make a horizontal, vertical, or
    diagonal sequence of size k to win the game.

TicTacToe:
    Standard Tic-Tac-Toe game.

FrozenLake:
    (disabled)
    A frozen lake with cracks in it! (uses legacy ValueSet instead of
    FeatureSet)

WindyGridworld:
    (disabled)
    A grid with displacement of `agent` (as if wind blows)
    (uses legacy ValueSet instead of FeatureSet)
'''
